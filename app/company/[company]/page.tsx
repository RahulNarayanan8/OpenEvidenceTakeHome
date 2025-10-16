'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'next/navigation';
import { Container, Typography, Paper, List, ListItem, ListItemText, CircularProgress, AppBar, Toolbar, Button } from '@mui/material';
import { Table, TableBody, TableCell, TableRow } from "@mui/material";


interface DiseaseSummary {
  disease: string;
  mentions: number;
  clicks: number;
  mentions_per_query: string;
  clicks_per_mention: number;
  times: number;
  monthly_category_cost: number;
  total_paid: number;
  clicks_per_dollar: number;
  mentions_per_day: number;
  clicks_per_day: number;
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
    <Typography>Company not found.</Typography>
  ) : (
    <>
      {/* Pie Charts */}
      <Paper elevation={3} style={{ padding: '1rem', marginBottom: '2rem' }}>
        <Typography variant="h5" gutterBottom>
          Category Revenue & Clicks
        </Typography>
        <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '250px' }}>
            <Typography variant="subtitle1">Total Paid per Category</Typography>
            <img
              src={`http://localhost:8000/pie/total_paid/${company}`} // pass company if your endpoint supports it
              alt="Total Paid Pie Chart"
              style={{ width: '100%', height: 'auto' }}
            />
          </div>
          <div style={{ flex: 1, minWidth: '250px' }}>
            <Typography variant="subtitle1">Total Clicks per Category</Typography>
            <img
              src={`http://localhost:8000/pie/total_clicks/${company}`} // pass company if your endpoint supports it
              alt="Total Clicks Pie Chart"
              style={{ width: '100%', height: 'auto' }}
            />
          </div>
        </div>
      </Paper>

      {/* Disease Category Metrics */}
      <Paper elevation={3} style={{ padding: '1rem' }}>
        <Typography variant="h5" gutterBottom>
          Purchased Disease Categories
        </Typography>
        <List>
          {data.map((item, idx) => (
            <ListItem key={idx} divider>
              <ListItemText
                primary={<Typography variant="h6">{item.disease}</Typography>}
                secondary={
                    <Table size="small" sx={{ mt: 1, mb: 1 }}>
                    <TableBody>
                      <TableRow>
                        <TableCell>Percentage of Queries Mentioning Disease</TableCell>
                        <TableCell align="right">{item.mentions_per_query}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Click Through Rate</TableCell>
                        <TableCell align="right">{item.clicks_per_mention.toFixed(2)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Average Time Spent Per Query</TableCell>
                        <TableCell align="right">{item.times.toFixed(2)} seconds</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Monthly Category Cost</TableCell>
                        <TableCell align="right">${item.monthly_category_cost.toFixed(2)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Total Paid for Category</TableCell>
                        <TableCell align="right">${item.total_paid.toFixed(2)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Clicks Per Dollar</TableCell>
                        <TableCell align="right">{item.clicks_per_dollar.toFixed(2)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Mentions Per Day</TableCell>
                        <TableCell align="right">{item.mentions_per_day.toFixed(2)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Clicks Per Day</TableCell>
                        <TableCell align="right">{item.clicks_per_day.toFixed(2)}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </>
  )}
</Container>
    </>
  );
}