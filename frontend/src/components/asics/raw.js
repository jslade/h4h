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
    queryFn: () => api.GET({ path:`/asic/${params.name}/raw`}).then((d) => d),
  })
  const {isPending: isPendingExtended, error: errorExtended, data: dataExtended} = useQuery({
    queryKey: ['asic/raw/extended', params.name],
    queryFn: () => api.GET({ path:`/asic/${params.name}/raw/extended`}).then((d) => d),
  })
  const {isPending: isPendingErrors, error: errorErrors, data: dataErrors} = useQuery({
    queryKey: ['asic/raw/errors', params.name],
    queryFn: () => api.GET({ path:`/asic/${params.name}/raw/errors`}).then((d) => d),
  })

  function render_json(x) {
    return <ReactJson src={x} />
  }
  
  return (
    <div>
      <h1>ASIC: {`${params.name}`} (raw data)</h1>
      {isPending ? `Loading ${params.name}...` : (error?.message || render_json(data))}
      <h3>ASIC: {`${params.name}`} (extended data)</h3>
      {isPendingExtended ? `Loading ${params.name}...` : (errorExtended?.message || render_json(dataExtended))}
      <h3>ASIC: {`${params.name}`} (errors)</h3>
      {isPendingErrors ? `Loading ${params.name}...` : (errorErrors?.message || render_json(dataErrors))}
    </div>
  )
}
