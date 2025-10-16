'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Container,
  Typography,
  Paper,
  CircularProgress,
  Box,
  AppBar,
  Toolbar,
  Button,
} from '@mui/material';

export default function RevenuePage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRevenue = async () => {
      try {
        const res = await axios.get('http://localhost:8000/revenue');
        setData(res.data);
      } catch (err) {
        console.error('Error fetching revenue data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchRevenue();
  }, []);

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" style={{ flexGrow: 1 }}>
            OpenEvidence Revenue Dashboard
          </Typography>
          <Button color="inherit" href="/">Back to Main</Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" style={{ marginTop: '2rem' }}>
        {loading ? (
          <CircularProgress />
        ) : (
          data && (
            <Paper elevation={3} style={{ padding: '2rem' }}>
              <Typography variant="h5" gutterBottom>
                Financial Summary
              </Typography>

              <Typography variant="body1">
                <strong>Total API costs:</strong> ${data.total_api_costs_usd}
              </Typography>
              <Typography variant="body1">
                <strong>Total Ad revenue:</strong> ${data.total_prorated_ad_revenue_usd}
              </Typography>
              <Typography variant="body1">
                <strong>Net Profit:</strong> ${data.net_profit_usd}
              </Typography>
              <Typography variant="body1">
                <strong>Profit Per Day:</strong> ${data.profit_per_day}
              </Typography>

              <Box mt={4}>
                <Typography variant="h6" gutterBottom>
                  Revenue Breakdown by Company
                </Typography>
                <ul>
                  {Object.entries(data.revenue_breakdown_by_company).map(([company, value]) => (
                    <li key={company}>
                      {company}: ${Number(value || 0).toFixed(2)}
                    </li>
                  ))}
                </ul>
              </Box>

              <Box mt={4} display="flex" justifyContent="center">
                <img
                  src="http://localhost:8000/revenue_chart"
                  alt="Revenue Pie Chart"
                  style={{ width: '80%', borderRadius: '12px' }}
                />
              </Box>
            </Paper>
          )
        )}
      </Container>
    </>
  );
}