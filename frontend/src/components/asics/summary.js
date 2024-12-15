import React from 'react'
import { useQuery } from '@tanstack/react-query'

import SummaryCard from './summary_card'

import API from '../../api';

const api = new API();

export default function Summary() {
    const {isLoading, error, data: active_data} = useQuery({
        queryKey: ['asic/active'],
        queryFn: () => api.GET({ path:`/asic/active`}).then((data) => data),
        refetchInterval: 60_000
    })
    
    function renderSummary(active_data) {
        return (<ul>
            {active_data.asics.map((name) => <><SummaryCard key={name} name={name} /><br/></>)}
        </ul>);
    }

    return (
      <div>
        {isLoading? "Loading..." : renderSummary(active_data)}
      </div>
    )
  }
  