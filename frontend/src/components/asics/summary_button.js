import React from 'react'
import { useQuery } from '@tanstack/react-query'

import ReactJson from '@microlink/react-json-view'

import API from '../../api';
import { useParams } from 'react-router-dom';

const api = new API();
window.API = api;


export default function Raw() {
  let params = useParams();
  const {isPending, error, data} = useQuery({
    queryKey: ['asic/summary-button', params.name],
    queryFn: () => api.GET({ path:`/asic/summary-button/${params.name}`}).then((data) => data),
  })

  return (
    <div>
      
    </div>
  )
}
