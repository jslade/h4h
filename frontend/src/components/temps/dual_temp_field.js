import React from 'react'
import { celcius_to_fahrenheit } from '../../utils/temps'

export default function DualTempField({deg_c}) {

  return (
    <span>{celcius_to_fahrenheit(deg_c)}{"\u00B0F"} ({deg_c}{"\u00B0C"})</span>
  )
}
