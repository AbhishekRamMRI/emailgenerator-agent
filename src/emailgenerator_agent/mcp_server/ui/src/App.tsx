import { useEffect, useState } from "react";
import { App as McpApp } from "@modelcontextprotocol/ext-apps";
import "./App.css";

function App() {
  // --------------------------------------------------
  // Email request state
  // --------------------------------------------------

  const [tone, setTone] = useState("professional");
  const [context, setContext] = useState("");
  const [dataPoints, setDataPoints] = useState("");

  // Generated email state

  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");

  // --------------------------------------------------
  // UI state
  // --------------------------------------------------

  const [status, setStatus] = useState("Ready");
  const [validation, setValidation] = useState("");
  const [isConnected, setIsConnected] = useState(false);

  // --------------------------------------------------
  // MCP App
  // --------------------------------------------------

  const [mcpApp] = useState(
    () =>
      new McpApp({
        name: "AI Email Generator",
        version: "1.0.0",
      })
  );

  
  // Connect MCP App to the MCP Host
  useEffect(() => {
    let mounted = true;

    const connect = async () => {
      try {
        setStatus("Connecting to MCP host...");

        await mcpApp.connect();

        if (mounted) {
          setIsConnected(true);
          setStatus("Ready");
        }
      } catch (error) {
        console.error("Failed to connect to MCP host:", error);

        if (mounted) {
          setIsConnected(false);
          setStatus("MCP connection failed");
        }
      }
    };

    connect();

    return () => {
      mounted = false;
      mcpApp.close();
    };
  }, [mcpApp]);

  // --------------------------------------------------
  // Generate Email
  // --------------------------------------------------
  //validate Data Point
  const isMeaningfulDataPoint = (point: string) => {  
    const cleaned = point.replace(/[^a-zA-Z0-9\s]/g, "").trim();

    return cleaned.length >= 3 && /[a-zA-Z]/.test(cleaned);
  };

  const handleGenerate = async () => {
    const data_points =
      dataPoints
        .match(/[^.!?]+[.!?]+|[^.!?]+$/g)
        ?.map((item) => item.trim())
        .filter(Boolean) ?? [];

    const invalidDataPoints = data_points.filter(
      (point) => !isMeaningfulDataPoint(point)
    );

    // Clear previous generated email
    setSubject("");
    setBody("");
    setValidation("");

    if (
      !tone.trim() ||
      !context.trim() ||
      data_points.length === 0
    ) {
      setStatus("Missing input");
      setValidation(
        "Please provide tone, context, and at least one data point."
      );
      return;
    }

    if (invalidDataPoints.length > 0) {
      setStatus("Invalid data points");
      setValidation(
        "Please enter meaningful information in the data points."
      );
      return;
    }

    setStatus("Generating...");

    try {
    // existing callServerTool code...
      const result = await mcpApp.callServerTool({
        name: "generate_email",
        arguments: {
          tone,
          context,
          data_points,
        },
      });

      console.log("MCP result:", result);

      const data = result.structuredContent as {
        subject?: string;
        body?: string;
        status?: string;
        validation_result?: {
          valid?: boolean;
          issues?: string[];
        };
      };

      setSubject(data.subject ?? "");
      setBody(data.body ?? "");

      if (data.validation_result?.valid) {
        setValidation("✓ Email passed validation");
      } else {
        const issues =
          data.validation_result?.issues ?? [];

        setValidation(
          issues.length > 0
            ? `✗ ${issues.join(" ")}`
            : "✗ Email failed validation"
        );
      }

      setStatus("Generated");
    } catch (error) {
      console.error("Generate email failed:", error);

      setStatus("Generation failed");

      setValidation(
        error instanceof Error
          ? error.message
          : String(error)
      );
    }
  };

  // --------------------------------------------------
  // Approve Email
  // --------------------------------------------------

  const handleApprove = async () => {
    console.log("[APP] Approve clicked");
    console.log("[APP] Connected:", isConnected);
    console.time("[APP] approve_email");

    if (!isConnected) {
      setStatus("MCP is still connecting...");
      return;
    }

    if (!subject.trim() || !body.trim()) {
      setStatus("No email to approve");
      return;
    }

    setStatus("Sending...");

    try {
      console.time("[APP] callServerTool");

      const result = await mcpApp.callServerTool({
        name: "approve_email",
        arguments: {
          subject,
          body,
        },
      });

      console.timeEnd("[APP] callServerTool");

      console.log("[APP] Approve result:", result);

      const data = result.structuredContent as {
        status?: string;
        message?: string;
      };

      setStatus(data.message ?? "Email has been sent");
    } catch (error) {
      console.error("[APP] Approve failed:", error);

      setStatus(
        error instanceof Error
          ? error.message
          : "Failed to send email"
      );
    } finally {
      console.timeEnd("[APP] approve_email");
    }
  };

  // --------------------------------------------------
  // Reject Email
  // --------------------------------------------------

  const handleReject = async () => {
    console.log("[APP] Reject clicked");
    console.log("[APP] Connected:", isConnected);
    console.time("[APP] reject_email");

    if (!isConnected) {
      setStatus("MCP is still connecting...");
      return;
    }

    if (!subject.trim() || !body.trim()) {
      setStatus("No email to reject");
      return;
    }

    setStatus("Rejecting...");

    try {
      console.time("[APP] callServerTool");

      const result = await mcpApp.callServerTool({
        name: "reject_email",
        arguments: {
          subject,
          body,
        },
      });

      console.timeEnd("[APP] callServerTool");

      console.log("[APP] Reject result:", result);

      const data = result.structuredContent as {
        status?: string;
        message?: string;
      };

      setStatus(data.message ?? "Email has been rejected");
    } catch (error) {
      console.error("[APP] Reject failed:", error);

      setStatus(
        error instanceof Error
          ? error.message
          : "Failed to reject email"
      );
    } finally {
      console.timeEnd("[APP] reject_email");
    }
  };

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  const infoPoints = dataPoints
    .split("\n")
    .map((point) => point.trim())
    .filter(Boolean);

  return (
    <div className="app">
      <div className="container">

        {/* Header */}

        <header className="app-header">
          <div className="app-header__content">
            <h1>AI Email Generator</h1>

            <p>
              Generate, review and approve professional emails
              using AI.
            </p>
          </div>
        </header>

        {/* Email Request */}

        <section className="card">
          <h2>Email Request</h2>

          <label htmlFor="tone">
            Tone
          </label>

          <select
            id="tone"
            value={tone}
            onChange={(event) =>
              setTone(event.target.value)
            }
          >
            <option value="professional">
              Professional
            </option>

            <option value="formal">
              Formal
            </option>

            <option value="assertive">
              Assertive
            </option>

            <option value="empathetic">
              Empathetic
            </option>

            <option value="friendly">
              Friendly
            </option>
          </select>

          <label htmlFor="context">
            Context
          </label>

          <textarea
            id="context"
            value={context}
            onChange={(event) =>
              setContext(event.target.value)
            }
            placeholder="Describe what the email is about..."
            rows={4}
          />

          <label htmlFor="dataPoints">
            Data Points
          </label>

          <textarea
            id="dataPoints"
            value={dataPoints}
            onChange={(event) =>
              setDataPoints(event.target.value)
            }
            placeholder="Enter one data point per line..."
            rows={6}
          />

          <button
            className="primary-button"
            onClick={handleGenerate}
            disabled={!isConnected}
          >
            Generate Email
          </button>
        </section>

        {/* Generated Email */}

        <section className="card">

          <div className="section-header">
            <h2>Review & Edit Email</h2>

            <span className="status">
              {status}
            </span>
          </div>

          <div className="mail-preview">
            <label htmlFor="subject">
              Subject:
            </label>

            <input
              id="subject"
              value={subject}
              onChange={(event) =>
                setSubject(event.target.value)
              }
              placeholder="Generated subject..."
            />

            <label htmlFor="body">
              Body:
            </label>

            <textarea
              id="body"
              value={body}
              onChange={(event) =>
                setBody(event.target.value)
              }
              placeholder="Generated email body..."
              rows={12}
            />

            <div className="mail-info">
              <label>
                Info Points:
              </label>

              {infoPoints.length > 0 ? (
                <ul>
                  {infoPoints.map((point, index) => (
                    <li key={`${point}-${index}`}>
                      {point}
                    </li>
                  ))}
                </ul>
              ) : (
                <p>
                  Add data points above to show
                  key highlights here.
                </p>
              )}
            </div>
          </div>

          <label>
            Validation
          </label>

          <div className="validation">
            {validation || "Not validated yet"}
          </div>

          <div className="actions">

            <button
              className="approve-button"
              onClick={handleApprove}
              disabled={!isConnected || !subject.trim() || !body.trim()}
            >
              Approve & Send
            </button>

            <button
              className="reject-button"
              onClick={handleReject}
              disabled={!isConnected || !subject.trim() || !body.trim()}
            >
              Reject
            </button>

          </div>

        </section>

      </div>
    </div>
  );
}

export default App;
