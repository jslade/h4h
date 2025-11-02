import React from "react";
import { useQuery } from "@tanstack/react-query";

import API from "../../api";

import { Link, Card } from "@mui/material";
import { styled } from "@mui/material/styles";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Unstable_Grid2";

import DualTempField from "../temps/dual_temp_field";
import { to_locale_string } from "../../utils/times";

const api = new API();

const Item = styled(Card)(({ theme, align }) => ({
  //backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(0.3),
  textAlign: align || "center",
  color:
    align === "right"
      ? theme.palette.text.secondary
      : theme.palette.text.primary,
}));

export default function SummaryCard({ name }) {
  const {
    isLoading,
    isFetching,
    data: asic_summary,
  } = useQuery({
    queryKey: ["asic/summary", name],
    queryFn: () =>
      api.GET({ path: `/asic/${name}/summary` }).then((data) => data),
    refetchInterval: 60_000,
  });

  if (isLoading) {
    return <h2>Loading {name}</h2>;
  }

  return (
    <Box
      sx={{ flexGrow: 1 }}
      className={`summary-card summary-status-${asic_summary.status}`}
    >
      <Grid container spacing={1}>
        <Grid xs={8}>
          <Item
            align="left"
            className={`summary-status-${asic_summary.status}`}
          >
            {asic_summary.name}
            {isFetching && " (fetching)"}
          </Item>
        </Grid>
        <Grid xs={2}>
          <Item align="right">
            <Link href={`/asics/raw/${asic_summary.name}`} target="_blank">
              see raw
            </Link>
          </Item>
        </Grid>
        <Grid xs={2}>
          <Item align="right">
            <Link href={`/asics/override/${asic_summary.name}`} target="_blank">
              override
            </Link>
          </Item>
        </Grid>

        <Grid xs={3}>
          <Item align="right">Status:</Item>
        </Grid>
        <Grid xs={9}>
          <Item align="left">
            {asic_summary.status}, since&nbsp;
            {to_locale_string(asic_summary.changed_at)}
          </Item>
        </Grid>

        <Grid xs={3}>
          <Item align="right">Interval:</Item>
        </Grid>
        <Grid xs={9}>
          <Item align="left">
            {asic_summary.interval_name
              ? asic_summary.interval_name +
                " until " +
                to_locale_string(asic_summary.interval_until)
              : "(none)"}
          </Item>
        </Grid>

        <Grid xs={3}>
          <Item align="right">Changed:</Item>
        </Grid>
        <Grid xs={9}>
          <Item align="left">
            {asic_summary.interval_changed_at
              ? to_locale_string(asic_summary.interval_changed_at)
              : "--"}
          </Item>
        </Grid>

        <Grid xs={3}>
          <Item align="right">Updated&nbsp;at:</Item>
        </Grid>
        <Grid xs={9}>
          <Item align="left">
            <span
              title={"Sampled at " + to_locale_string(asic_summary.sampled_at)}
            >
              {to_locale_string(asic_summary.updated_at)}
            </span>
          </Item>
        </Grid>

        <Grid xs={3}>
          <Item align="right">Hashrate:</Item>
        </Grid>
        <Grid xs={9}>
          <Item align="left">{asic_summary.hash_rate} TH/s</Item>
        </Grid>

        <Grid xs={3}>
          <Item align="right">Power:</Item>
        </Grid>
        <Grid xs={9}>
          <Item align="left">
            {asic_summary.power} W / {asic_summary.power_limit} W
          </Item>
        </Grid>

        <Grid xs={3}>
          <Item align="right">Efficiency:</Item>
        </Grid>
        <Grid xs={9}>
          <Item align="left">{asic_summary.power_per_th} W/TH</Item>
        </Grid>

        <Grid xs={3}>
          <Item align="right">Int&nbsp;temp:</Item>
        </Grid>
        <Grid xs={9}>
          <Item align="left">
            <DualTempField deg_c={asic_summary.temp} />
          </Item>
        </Grid>

        <Grid xs={3}>
          <Item align="right">Env&nbsp;temp:</Item>
        </Grid>
        <Grid xs={9}>
          <Item align="left">
            <DualTempField deg_c={asic_summary.env_temp} />
          </Item>
        </Grid>
      </Grid>
    </Box>
  );
}
