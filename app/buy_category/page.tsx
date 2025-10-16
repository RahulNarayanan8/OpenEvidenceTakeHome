'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Typography, TextField, MenuItem, Button, Paper, Snackbar, Alert } from '@mui/material';

export default function BuyCategoryPage() {
  const [categories, setCategories] = useState<any[]>([]);
  const [selectedDisease, setSelectedDisease] = useState('');
  const [company, setCompany] = useState('');
  const [bidPrice, setBidPrice] = useState('');
  const [adImage, setAdImage] = useState('');
  const [adLink, setAdLink] = useState('');
  const [message, setMessage] = useState('');
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const fetchCategories = async () => {
      const res = await axios.get('http://localhost:8000/categories_ads');
      setCategories(Object.entries(res.data));
    };
    fetchCategories();
  }, []);

  const handleSubmit = async () => {
    try {
      const res = await axios.post('http://localhost:8000/purchase_category', {
        disease: selectedDisease,
        company,
        bid_price: bidPrice,
        ad_image: adImage,
        ad_link: adLink,
      });
      setMessage(res.data.message);
    } catch (err: any) {
      setMessage(err.response?.data?.error || 'Purchase failed');
    } finally {
      setOpen(true);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 5 }}>
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Typography variant="h5" gutterBottom>Purchase Disease Category</Typography>

        <TextField
          select
          label="Select Disease"
          fullWidth
          margin="normal"
          value={selectedDisease}
          onChange={(e) => setSelectedDisease(e.target.value)}
        >
          {categories.map(([disease, data]) => (
            <MenuItem key={disease} value={disease}>
              {disease} — Current: ${data.category_cost} / Month (Owned by {data.company})
            </MenuItem>
          ))}
        </TextField>

        <TextField label="Your Company Name" fullWidth margin="normal" value={company} onChange={(e) => setCompany(e.target.value)} />
        <TextField label="Your Bid Price ($)" fullWidth margin="normal" value={bidPrice} onChange={(e) => setBidPrice(e.target.value)} />
        <TextField label="Ad Image Path (Relative Path) (Ex: ad_images/genentech_allergy.png)" fullWidth margin="normal" value={adImage} onChange={(e) => setAdImage(e.target.value)} />
        <TextField label="Ad Link (URL)" fullWidth margin="normal" value={adLink} onChange={(e) => setAdLink(e.target.value)} />

        <Button
          variant="contained"
          color="primary"
          fullWidth
          sx={{ mt: 2 }}
          onClick={handleSubmit}
          disabled={!selectedDisease || !company || !bidPrice}
        >
          Purchase
        </Button>
      </Paper>

      <Snackbar open={open} autoHideDuration={5000} onClose={() => setOpen(false)}>
        <Alert onClose={() => setOpen(false)} severity="info">
          {message}
        </Alert>
      </Snackbar>
    </Container>
  );
}