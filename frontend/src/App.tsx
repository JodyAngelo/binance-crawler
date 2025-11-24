import { useEffect, useMemo, useState } from "react";

interface DateRange {
  from: string;
  to: string;
}

type InstrumentMap = Record<string, DateRange | Record<string, DateRange>>;
type CategoryMap = Record<string, InstrumentMap>;
type FrequencyMap = Record<string, CategoryMap>;
type BinanceData = Record<string, FrequencyMap>;

export default function App() {
  const [data, setData] = useState<BinanceData | null>(null);
  const [selectedFrequency, setSelectedFrequency] = useState<string | null>(
    null
  );
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedInstrument, setSelectedInstrument] = useState<string | null>(
    null
  );
  const [selectedTimeFrame, setSelectedTimeframe] = useState<string | null>(
    null
  );
  const frequencies = useMemo(() => (data ? Object.keys(data) : []), [data]);

  const categories = useMemo(() => {
    return data && selectedFrequency
      ? Object.keys(data[selectedFrequency])
      : [];
  }, [data, selectedFrequency]);

  const instruments = useMemo(() => {
    return data && selectedFrequency && selectedCategory
      ? Object.keys(data[selectedFrequency][selectedCategory])
      : [];
  }, [data, selectedFrequency, selectedCategory]);

  const instrumentDatas = useMemo(() => {
    return data && selectedFrequency && selectedCategory && selectedInstrument
      ? data[selectedFrequency][selectedCategory][selectedInstrument]
      : null;
  }, [data, selectedFrequency, selectedCategory, selectedInstrument]);

  const timeframes = useMemo(() => {
    if (!instrumentDatas) return null;
    if ("from" in instrumentDatas && "to" in instrumentDatas) return null;

    return Object.keys(instrumentDatas);
  }, [instrumentDatas]);

  const result = useMemo(() => {
    if (!instrumentDatas) return null;
    if (selectedTimeFrame && instrumentDatas[selectedTimeFrame]) {
      return {
        label: selectedTimeFrame,
        from: instrumentDatas[selectedTimeFrame].from,
        to: instrumentDatas[selectedTimeFrame].to,
      };
    }

    if (
      !selectedTimeFrame &&
      "from" in instrumentDatas &&
      "to" in instrumentDatas
    ) {
      return {
        label: selectedTimeFrame,
        from: instrumentDatas.from,
        to: instrumentDatas.to,
      };
    }

    return null;
  }, [instrumentDatas, selectedTimeFrame]);

  useEffect(() => {
    const websocket = new WebSocket("ws://localhost:8001");

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data);
      setData(data);
    };

    return () => websocket.close();
  }, []);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "16px",
        marginTop: "40px",
      }}
    >
      <select
        value={selectedFrequency ?? ""}
        onChange={(e) => {
          setSelectedFrequency(e.target.value);
          setSelectedCategory(null);
          setSelectedInstrument(null);
          setSelectedTimeframe(null);
        }}
        style={{ width: "250px", padding: "10px", borderRadius: "6px" }}
      >
        <option value="">Select frequency</option>
        {frequencies.map((frequency) => (
          <option key={frequency}>{frequency}</option>
        ))}
      </select>

      <select
        value={selectedCategory ?? ""}
        onChange={(e) => {
          setSelectedCategory(e.target.value);
          setSelectedInstrument(null);
          setSelectedTimeframe(null);
        }}
        style={{ width: "250px", padding: "10px", borderRadius: "6px" }}
      >
        <option value="">Select category</option>
        {categories.map((category) => (
          <option key={category}>{category}</option>
        ))}
      </select>

      <select
        value={selectedInstrument ?? ""}
        onChange={(e) => {
          setSelectedInstrument(e.target.value);
          setSelectedTimeframe(null);
        }}
        style={{ width: "250px", padding: "10px", borderRadius: "6px" }}
      >
        <option value="">Select instrument</option>
        {instruments.map((instrument) => (
          <option key={instrument}>{instrument}</option>
        ))}
      </select>

      {timeframes && (
        <div>
          {timeframes.map((timeframe) => (
            <button
              key={timeframe}
              onClick={() => setSelectedTimeframe(timeframe)}
              style={{
                padding: "6px 12px",
                margin: "4px",
                borderRadius: "6px",
                background: "#161616",
                color: "white",
              }}
            >
              {timeframe}
            </button>
          ))}
        </div>
      )}

      {result && (
        <div
          style={{
            marginTop: "24px",
            padding: "18px 20px",
            borderRadius: "14px",
            background: "#161616",
            color: "#e5e5e5",
            width: "300px",
            textAlign: "left",
          }}
        >
          <div style={{ display: "flex", flexDirection: "column", gap: "3px" }}>
            {result.label ? (
              <h5 style={{ margin: 0 }}>{`Timeframe: ${result.label}`}</h5>
            ) : null}

            <h5 style={{ margin: 0 }}>{`From: ${result.from}`}</h5>
            <h5 style={{ margin: 0 }}>{`To: ${result.to}`}</h5>
          </div>
        </div>
      )}
    </div>
  );
}
