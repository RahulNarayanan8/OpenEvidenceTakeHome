'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Container,
  Typography,
  Paper,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  AppBar,
  Toolbar,
  Button,
  Box
} from '@mui/material';

interface UnclaimedDisease {
  disease: string;
  mentions: number;
}

export default function CategoriesForSale() {
  const [diseases, setDiseases] = useState<UnclaimedDisease[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchDiseases = async () => {
      try {
        const res = await axios.get('http://localhost:8000/categories_for_sale');
        setDiseases(res.data.unclaimed_diseases);
      } catch (error) {
        console.error('Error fetching unclaimed diseases:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchDiseases();
  }, []);

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" style={{ flexGrow: 1 }}>
            Categories For Sale
          </Typography>
          <Button color="inherit" href="/">Back to Main</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" style={{ marginTop: '2rem' }}>
        <Typography variant="h5" gutterBottom>
          Most Mentioned Unclaimed Disease Categories
        </Typography>

        {loading ? (
          <CircularProgress />
        ) : !diseases || diseases.length === 0 ? (
          <Typography variant="body1" color="textSecondary">
            No unclaimed categories yet.
          </Typography>
        ) : (
          <>
            <Paper elevation={3} style={{ padding: '1rem', marginBottom: '2rem' }}>
              <List>
                {diseases.map((item, idx) => (
                  <ListItem key={idx} divider>
                    <ListItemText
                      primary={<Typography variant="h6">{item.disease}</Typography>}
                      secondary={`Mentions: ${item.mentions}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>

            {/* --- Bar Chart Section --- */}
            <Paper elevation={3} style={{ padding: '1rem' }}>
              <Typography variant="h6" gutterBottom>
                Visual Representation
              </Typography>
              <Box display="flex" justifyContent="center" alignItems="center">
                <img
                  src="http://localhost:8000/categories_for_sale_chart"
                  alt="Unclaimed Categories Bar Chart"
                  style={{
                    maxWidth: '100%',
                    height: 'auto',
                    borderRadius: '8px',
                    boxShadow: '0px 2px 8px rgba(0,0,0,0.2)'
                  }}
                />
              </Box>
            </Paper>
          </>
        )}
      </Container>
    </>
  );
}