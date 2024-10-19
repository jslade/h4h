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
    queryFn: () => api.GET({ path:`/asic/${params.name}/raw/extended`}).then((d) => d),
  })
  const {isPendingExtended, errorExtended, dataExtended} = useQuery({
    queryKey: ['asic/raw/extended', params.name],
    queryFn: () => api.GET({ path:`/asic/${params.name}/raw`}).then((d) => d),
  })

  function render_json(d) {
    return <ReactJson src={d} />
  }
  
  return (
    <div>
      <h1>ASIC: {`${params.name}`} (raw data)</h1>
      {isPending ? `Loading ${params.name}...` : (error?.message || render_json(data))}
      {isPendingExtended ? `Loading ${params.name}...` : (errorExtended?.message || render_json(dataExtended))}
    </div>
  )
}
