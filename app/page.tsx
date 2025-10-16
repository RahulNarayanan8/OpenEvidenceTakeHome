'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  TextField,
  Button,
  Typography,
  Paper,
  List,
  CircularProgress,
  Box,
  AppBar,
  Toolbar,
} from '@mui/material';
import { styled } from '@mui/system';

interface HistoryItem {
  role: string;
  content: string;
}

const StyledPaper = styled(Paper)({
  padding: '1rem',
  marginTop: '1rem',
  marginBottom: '1rem',
  fontFamily: 'Open Sans, sans-serif',
});

const StyledButton = styled(Button)({
  height: '56px', // to match TextField height
});

const FixedAppBar = styled(AppBar)({
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  zIndex: 1100,
});

export default function Home() {
  const [ad, setAd] = useState<any>(null);
  const [question, setQuestion] = useState<string>('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [answer, setAnswer] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const scrollToBottom = () => {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: 'smooth',
    });
  };

  const fetchAd = async (query: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/get_ad`, {
        params: { query },
      });
      return response.data.ad;
    } catch (error) {
      console.error('Error fetching ad:', error);
      return null;
    }
  };

  const handleAdClick = async () => {
    try {
      await axios.post("http://localhost:8000/track_click", {
        disease: ad.category,
        company: ad.company,
      });
    } catch (error) {
      console.error("Error tracking click:", error);
    } finally {
      window.open(ad.link, "_blank");
    }
  };


  const DISEASES = ["arthritis", "meningitis", "pneumonia", "breast cancer", "lung cancer", "melanoma", "allergy", "asthma", "hiv", "diabetes", "obesity", "pancreatic cancer"];

  const identifyKeywords = (query: string) => {
    const lower = query.toLowerCase();
    return DISEASES.filter((d) => lower.includes(d));
  };

  const [startTime, setStartTime] = useState<number | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    scrollToBottom();
  
    // 1️⃣ Track start time
    const now = Date.now();
    setStartTime(now);
  
    try {
      // 2️⃣ Fetch ad
      const adData = await fetchAd(question);
      setAd(adData);
  
      // 3️⃣ Fetch answer
      const response = await axios.post('/api/ask', { question, history });
  
      // 4️⃣ Calculate query duration
      const endTime = Date.now();
      const duration = endTime - now;
  
      // 5️⃣ Identify diseases
      const diseases = identifyKeywords(question);
  
      // 6️⃣ Log time to backend
      if (diseases.length > 0) {
        await axios.post('http://localhost:8000/log_query_time', {
          diseases,
          duration_ms: duration
        });
      }
  
      // 7️⃣ Update chat history
      setHistory([
        ...history,
        { role: 'user', content: question },
        { role: 'assistant', content: response.data.answer },
      ]);
      setAnswer(response.data.answer);
      setQuestion('');
    } catch (error) {
      console.error('Error fetching the answer:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = () => {
    setHistory([]);
    setAnswer('');
    setQuestion('');
    setAd(null);
    scrollToBottom();
  };

  useEffect(() => {
    if (!loading) {
      scrollToBottom();
    }
  }, [loading, history]);

  return (
    <>
      <FixedAppBar position="static">
        <Container maxWidth="md">
          <Toolbar disableGutters>
            <Typography
              variant="h6"
              style={{ flexGrow: 1, fontFamily: 'Roboto, sans-serif' }}
            >
              Simple Ask
            </Typography>
            <Button color="inherit" onClick={handleNewConversation}>
              New Conversation
            </Button>
          </Toolbar>
        </Container>
      </FixedAppBar>

      <Container
        maxWidth="lg"
        style={{
          marginTop: '120px',
          fontFamily: 'Roboto, sans-serif',
          marginBottom: '250px',
          display: 'flex',
          gap: '2rem',
        }}
      >
        {/* Left side: chat */}
        <Box flex={3}>
          {history.length > 0 && (
            <List>
              {history.map((item, index) => (
                <StyledPaper elevation={3} key={index}>
                  <Typography variant="body1" component="div">
                    <strong>
                      {item.role.charAt(0).toUpperCase() + item.role.slice(1)}:
                    </strong>
                  </Typography>
                  <Box
                    component="div"
                    dangerouslySetInnerHTML={{
                      __html: item.content.replace(/\n/g, '<br />'),
                    }}
                  />
                </StyledPaper>
              ))}
            </List>
          )}

          <StyledPaper elevation={3}>
            <form
              onSubmit={handleSubmit}
              style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}
            >
              <TextField
                label="Ask a question"
                variant="outlined"
                fullWidth
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={loading}
              />
              <StyledButton
                type="submit"
                variant="contained"
                color="primary"
                disabled={loading}
              >
                Ask
              </StyledButton>
            </form>
          </StyledPaper>

          {loading && (
            <Box display="flex" justifyContent="center" alignItems="center" mt={2}>
              <CircularProgress />
            </Box>
          )}
        </Box>

        {/* Right side: persistent ad */}
        <Box
          flex={1}
          display="flex"
          flexDirection="column"
          alignItems="center"
          position="sticky"
          top="120px"
          height="fit-content"
        >
          {ad ? (
            <Paper
              elevation={4}
              style={{
                padding: '1rem',
                textAlign: 'center',
                borderRadius: '12px',
              }}
            >
              <a
                href={ad.link}
                target="_blank"
                rel="noopener noreferrer"
                style={{ textDecoration: 'none' }}
              >
                <img
                  src={
                    ad.ad_path.startsWith('http')
                      ? ad.ad_path
                      : `http://localhost:8000/${ad.ad_path}`
                  }
                  alt={`Ad from ${ad.company}`}
                  style={{
                    width: '100%',
                    borderRadius: '12px',
                    cursor: 'pointer',
                    marginBottom: '0.5rem',
                  }}
                  onClick={handleAdClick}
                  onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.02)')}
                  onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1.0)')}
                />
                <Typography variant="body2" color="textSecondary">
                  Sponsored by {ad.company}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {ad.category}
                </Typography>
              </a>
            </Paper>
          ) : (
            <Paper
              elevation={1}
              style={{
                padding: '1rem',
                textAlign: 'center',
                borderRadius: '12px',
                color: '#999',
              }}
            >
              <Typography variant="body2">No relevant ad</Typography>
            </Paper>
          )}
        </Box>
      </Container>
    </>
  );
}

