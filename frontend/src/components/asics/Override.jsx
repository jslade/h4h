import React from "react";

import API from "../../api";
import { useParams } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";

const api = new API();

export default function Override() {
  const params = useParams();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (formData) =>
      api.POST({
        path: `/asic/${params.name}/set-override`,
        body: formData
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries(["asic/summary", params.name]);
    },
    onError: (error) => {
      console.error("Error submitting override:", error);
      alert("Error submitting override.");
    },
  });

  const onSubmit = (e) => {
    e.preventDefault();
    const formData = {
      hashing: e.target.hashing.checked,
      hours: parseInt(e.target.hours.value, 10),
    };

    mutation.mutate(formData);
  };

  return (
    <div>
      <h1>ASIC: {`${params.name}`} override</h1>
      <form onSubmit={onSubmit}>
        <div>
          <label>
            Hashing:
            <input type="checkbox" name="hashing" defaultChecked={true} />
          </label>
        </div>
        <div>
          <label>
            Hours:
            <input type="number" name="hours" defaultValue={4} min={1} />
          </label>
        </div>
        <button type="submit">Set</button>
      </form>
    </div>
  );
}
