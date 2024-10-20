import React from 'react'
import { useQuery } from '@tanstack/react-query'

import Button from '@mui/material/Button'

import API from '../../api';

const api = new API();

export default function Summary() {
    const {isPending, error, data: summary_data} = useQuery({
        queryKey: ['asic/summary'],
        queryFn: () => api.GET({ path:`/asic/summary`}).then((data) => data),
        refetchInterval: 60_000
    })
    
    function renderSummary(summary_data) {
        return (<ul>
            {summary_data.asics.map((asic) => <li>{asic.name}: {asic.status} ({asic.updated_at})</li>)}
        </ul>);
    }

    return (
      <div>
        {isPending? "Loading..." : renderSummary(summary_data)}
      </div>
    )
  }
  