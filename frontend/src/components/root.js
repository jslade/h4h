import React from 'react'
import { useQuery } from '@tanstack/react-query'

import API from '../api';

const api = new API();
window.API = api;

export default function Root() {
  const {isPending, error, data} = useQuery({
    queryKey: ['test'],
    queryFn: () => api.GET({ path:"/test"}).then((data) => data),
  })

  return (
    <div>
      <h1>Hash for Heat</h1>
      <p>Test</p>
      <div>{isPending ? "Loading..." : (error?.message || JSON.stringify(data))}</div>
    </div>
  )
}
