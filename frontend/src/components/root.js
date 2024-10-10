import React from 'react'
import { useQuery } from '@tanstack/react-query'

import API from '../api';

const api = new API();


export default function Root() {
  const {isPending, error, summary_data} = useQuery({
    queryKey: ['asic/summary'],
    queryFn: () => api.GET({ path:`/asic/summary`}).then((data) => data),
  })

  function render_summaries(summary_data) {
    return <div/>
  }

  return (
    <div>
      <h1>Hash for Heat</h1>
      {isPending ? `Loading...` : (error?.message || render_summaries(summary_data))}
    </div>
  )
}
