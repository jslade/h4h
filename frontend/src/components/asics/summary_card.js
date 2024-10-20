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
      </ul>
    </Card>      
  )
}
