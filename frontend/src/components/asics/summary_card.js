import React from 'react'
import { Card } from '@mui/material';

export default function SummaryCard({asic_summary}) {

  return (
    <Card>
      <ul>
        <li>{asic_summary.name}</li>
        <li>status: {asic_summary.status}</li>
        <li>updated_at: {asic_summary.updated_at}</li>
        <li>changed_at: {asic_summary.changed_at}</li>
        <li>sampled_at: {asic_summary.sampled_at}</li>
        <li>hash_rate: {asic_summary.hash_rate}</li>
        <li>power: {asic_summary.power}</li>
        <li>power_limit: {asic_summary.power_limit}</li>
        <li>temp: {asic_summary.temp}</li>
        <li>env_temp: {asic_summary.env_temp}</li>
      </ul>
    </Card>      
  )
}
