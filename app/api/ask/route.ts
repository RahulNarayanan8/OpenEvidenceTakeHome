import OpenAI from 'openai';
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const client = new OpenAI({
  apiKey: process.env['OPENAI_API_KEY'],
});

const COSTS_PATH = path.join(process.cwd(), 'oe_ad_service/query_costs.json');


function logCost(cost: number, type: string) {
  let data: Record<string, number> = {};
  if (fs.existsSync(COSTS_PATH)) {
    data = JSON.parse(fs.readFileSync(COSTS_PATH, 'utf-8'));
  }

  // Accumulate total cost for each type
  data[type] = (data[type] || 0) + cost;

  fs.writeFileSync(COSTS_PATH, JSON.stringify(data, null, 2));
}


export async function POST(request: Request) {
  const { question, history } = await request.json();

  try {
    // Make the API call
    const chatCompletion = await client.chat.completions.create({
      messages: [...history, { role: 'user', content: question }],
      model: 'gpt-3.5-turbo',
    });

    const answer = chatCompletion.choices[0].message.content;
    const usage = chatCompletion.usage;

    const inputCostPer1K = 0.0005;
    const outputCostPer1K = 0.0015;

    const promptTokens = usage?.prompt_tokens || 0;
    const completionTokens = usage?.completion_tokens || 0;

    const totalCost =
      (promptTokens / 1000) * inputCostPer1K +
      (completionTokens / 1000) * outputCostPer1K;

    logCost(totalCost, 'query');

    return NextResponse.json({
      answer,
      cost_usd: totalCost,
      tokens: { promptTokens, completionTokens },
    });

  } catch (error: any) {
    console.error('Error in /api/ask route:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
