import React from 'react'
import { Link, Card } from '@mui/material';
import { styled } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Unstable_Grid2';

import DualTempField from '../temps/dual_temp_field';
import { to_locale_string } from '../../utils/times';

const Item = styled(Card)(({ theme, align }) => ({
  //backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(0.3),
  textAlign: align || 'center',
  color: align === 'right' ? theme.palette.text.secondary : theme.palette.text.primary,
}));


export default function SummaryCard({asic_summary}) {

  return (
    <Box sx={{ flexGrow: 1 }} className={`summary-card summary-status-${asic_summary.status}`}>
      <Grid container spacing={1}>
        <Grid xs={10} >
          <Item align="left" className={`summary-status-${asic_summary.status}`}>{asic_summary.name}</Item>
        </Grid>
        <Grid xs={2} >
          <Item align="right"><Link href={`/asics/raw/${asic_summary.name}`} target="_blank">see raw</Link></Item>
        </Grid>

        <Grid xs={3} >
          <Item align="right">Status:</Item>
        </Grid>
        <Grid xs={9} >
          <Item align="left"><span title={"Since " + to_locale_string(asic_summary.changed_at)}>{asic_summary.status}</span></Item>
        </Grid>

        <Grid xs={3} >
          <Item align="right">Updated at:</Item>
        </Grid>
        <Grid xs={9} >
          <Item align="left"><span title={"Sampled at " + to_locale_string(asic_summary.sampled_at)}>{to_locale_string(asic_summary.updated_at)}</span></Item>
        </Grid>

        <Grid xs={3} >
          <Item align="right">Hashrate:</Item>
        </Grid>
        <Grid xs={9} >
          <Item align="left">{asic_summary.hash_rate} TH/s</Item>
        </Grid>

        <Grid xs={3} >
          <Item align="right">Power:</Item>
        </Grid>
        <Grid xs={9} >
          <Item align="left">{asic_summary.power} W / {asic_summary.power_limit} W</Item>
        </Grid>

        <Grid xs={3} >
          <Item align="right">Efficiency:</Item>
        </Grid>
        <Grid xs={9} >
          <Item align="left">{asic_summary.power_per_th} TH/W</Item>
        </Grid>

        <Grid xs={3} >
          <Item align="right">Int temp:</Item>
        </Grid>
        <Grid xs={9} >
          <Item align="left"><DualTempField deg_c={asic_summary.temp} /></Item>
        </Grid>

        <Grid xs={3} >
          <Item align="right">Env temp:</Item>
        </Grid>
        <Grid xs={9} >
          <Item align="left"><DualTempField deg_c={asic_summary.env_temp} /></Item>
        </Grid>

        <Grid xs={3} >
          <Item align="right">Env temp:</Item>
        </Grid>
        <Grid xs={9} >
          <Item align="left"><DualTempField deg_c={asic_summary.env_temp} /></Item>
        </Grid>
      </Grid>
    </Box>      
  )
}
