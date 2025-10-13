'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'next/navigation';
import { Container, Typography, Paper, List, ListItem, ListItemText, CircularProgress, AppBar, Toolbar, Button } from '@mui/material';

interface DiseaseSummary {
  disease: string;
  mentions: number;
  clicks: number;
  times: number;
}

export default function CompanyPage() {
  const params = useParams();
  const company = params.company;
  const [data, setData] = useState<DiseaseSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await axios.get(`http://localhost:8000/company_summary/${company}`);
        setData(res.data.summary || []);
      } catch (err) {
        console.error('Error fetching company summary:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, [company]);

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" style={{ flexGrow: 1 }}>
            {company} Summary
          </Typography>
          <Button color="inherit" href="/">Back to Main</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" style={{ marginTop: '2rem' }}>
        {loading ? (
          <CircularProgress />
        ) : data.length === 0 ? (
          <Typography>No purchased categories found for this company.</Typography>
        ) : (
          <Paper elevation={3} style={{ padding: '1rem' }}>
            <Typography variant="h5" gutterBottom>
              Purchased Disease Categories
            </Typography>
            <List>
              {data.map((item, idx) => (
                <ListItem key={idx} divider>
                  <ListItemText
                    primary={item.disease}
                    secondary={`Mentions: ${item.mentions} | Clicks: ${item.clicks} | Time Spent: ${item.times}`}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}
      </Container>
    </>
  );
}