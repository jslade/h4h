import React from 'react'
import { useQuery } from '@tanstack/react-query'

import ReactJson from '@microlink/react-json-view'

import API from '../../api';
import { useParams } from 'react-router-dom';

const api = new API();

export default function Raw() {
  let params = useParams();
  const {isPending, error, data} = useQuery({
    queryKey: ['asic/raw', params.name],
    queryFn: () => api.GET({ path:`/asic/raw/${params.name}`}).then((data) => data),
  })

  function render_json(data) {
    return <ReactJson src={data} />
  }
  
  return (
    <div>
      <h1>ASIC: {`${params.name}`} (raw data)</h1>
      {isPending ? `Loading ${params.name}...` : (error?.message || render_json(data))}
    </div>
  )
}
