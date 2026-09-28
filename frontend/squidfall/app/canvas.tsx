import { useAgent } from "@copilotkit/react-core/v2";

type CanvasState = {
  title: string;
  items: { id: string; label: string; done: boolean }[];
  weather?: {
    location: string;
    lat: number;
    lon: number;
    forecast: string;
  };
};

export function Canvas() {
  const { agent } = useAgent({agentId: "squidfall"});
  const state = (agent.state ?? {}) as Partial<CanvasState>;
  return (
    <main className="canvas">
      <h1>{state.title ?? "Untitled"}</h1>
      <ul>
        {(state.items ?? []).map((item) => (
          <li key={item.id} data-done={item.done}>
            {item.label}
          </li>
        ))}
      </ul>
      {state.weather && (
        <p className="weather">
          {state.weather.location}: {state.weather.forecast}
        </p>
      )}
    </main>
  );
}