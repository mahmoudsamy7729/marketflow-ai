import { Link } from "react-router-dom";

const workflowSteps = [
  {
    id: "01",
    title: "Connect your channels",
    body: "Start with Facebook today, then expand into the multi-channel engine as your operation grows.",
  },
  {
    id: "02",
    title: "Set the campaign cadence",
    body: "Define intervals, volume, voice, and audience once so every generated post stays aligned.",
  },
  {
    id: "03",
    title: "Generate the plan and posts",
    body: "Turn campaign strategy into dated content plans, draft copy, and image-ready publishing assets.",
  },
  {
    id: "04",
    title: "Push into delivery flow",
    body: "Review, schedule, publish now, and move toward a fully automated queue without changing systems.",
  },
] as const;

const productSignals = [
  "Campaign -> plan -> posts -> schedule -> publish",
  "Facebook-first workflow live now",
  "AI content planning and post generation",
  "Built for lean teams that need operational speed",
] as const;

const outcomeRows = [
  {
    metric: "12 min",
    label: "From campaign brief to first draft batch",
  },
  {
    metric: "1 view",
    label: "Connected channels, cadence, queue, and activity in one surface",
  },
  {
    metric: "0 drift",
    label: "Strategy, copy, and publishing stay tied to the same campaign source",
  },
] as const;

const channelMatrix = [
  {
    name: "Facebook",
    state: "Live now",
    detail: "OAuth connection, page selection, image posting, and publish-now flow already wired into the product.",
  },
  {
    name: "Instagram",
    state: "Structured next",
    detail: "The campaign model already supports it, so expansion can happen without redesigning the workflow.",
  },
  {
    name: "WeChat",
    state: "Roadmapped",
    detail: "Channel-aware publishing is planned as the delivery layer widens beyond the current Facebook-first release.",
  },
] as const;

const proofPoints = [
  "JWT auth and multi-user access",
  "Campaign creation with cadence controls",
  "AI-generated content plans with dated items",
  "Post generation from plan items",
  "Image upload and remote image attachment",
  "Dashboard summary with campaign health",
] as const;

export function LandingPage() {
  return (
    <>
      <nav className="topbar">
        <div className="topbar-inner">
          <a className="brand" href="#top" aria-label="marektflow.ai home">
            <span className="brand-mark" />
            <span className="brand-name">marektflow.ai</span>
          </a>

          <div className="topbar-links">
            <a href="#workflow">Workflow</a>
            <a href="#engine">Engine</a>
            <a href="#launch">Launch</a>
          </div>

          <div className="topbar-actions">
            <Link className="topbar-auth-link" to="/login">
              Sign in
            </Link>
            <Link className="button button-secondary button-small" to="/register">
              Create account
            </Link>
          </div>
        </div>
      </nav>

      <header className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow reveal">
            AI marketing automation for campaigns that need to move with precision
          </p>

          <h1 className="hero-title reveal reveal-delay-1">
            Direct the signal.
            <span>Let the system ship the work.</span>
          </h1>

          <p className="hero-summary reveal reveal-delay-2">
            marektflow.ai gives lean teams one operating surface for campaign
            setup, AI content planning, post generation, and delivery
            orchestration. No more jumping between planners, docs, generators,
            and publishing tools.
          </p>

          <div className="hero-actions reveal reveal-delay-3">
            <Link className="button button-primary" to="/register">
              Create workspace
            </Link>
            <Link className="button button-secondary" to="/login">
              Sign in
            </Link>
          </div>

          <ul className="signal-list reveal reveal-delay-4" aria-label="Product signals">
            {productSignals.map((signal) => (
              <li key={signal}>{signal}</li>
            ))}
          </ul>
        </div>

        <div className="hero-visual" aria-hidden="true">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="orbit orbit-three" />

          <div className="hero-grid" />

          <div className="flow-stage">
            {workflowSteps.map((step, index) => (
              <div className="flow-node" key={step.id} style={{ ["--index" as string]: index }}>
                <span className="flow-id">{step.id}</span>
                <strong>{step.title}</strong>
                <span>{step.body}</span>
              </div>
            ))}
          </div>

          <div className="hero-note hero-note-primary">
            <span className="note-label">Active queue</span>
            <strong>Spring launch cadence locked</strong>
            <span>3 posts every 7 days across campaign dates</span>
          </div>

          <div className="hero-note hero-note-secondary">
            <span className="note-label">Generation ready</span>
            <strong>14 plan items mapped</strong>
            <span>Copy, imagery, and publish states tracked together</span>
          </div>
        </div>
      </header>

      <section className="ticker" aria-label="Platform capabilities">
        <div className="ticker-track">
          {productSignals.concat(productSignals).map((signal, index) => (
            <span key={`${signal}-${index}`}>{signal}</span>
          ))}
        </div>
      </section>

      <main>
        <section className="section section-workflow" id="workflow">
          <div className="section-heading">
            <p className="kicker">Workflow</p>
            <h2>One sequence. One source of truth.</h2>
          </div>

          <div className="workflow-layout">
            <div className="workflow-lead">
              <p>
                The system already supports the real authoring loop that matters:
                campaign setup, content plan generation, post creation, image
                attachment, and immediate publishing.
              </p>
              <p>
                The next step is deeper delivery automation, not another layer
                of disconnected tooling. That makes the product story clear and
                the landing page honest.
              </p>
            </div>

            <div className="workflow-rail">
              {workflowSteps.map((step) => (
                <article className="workflow-row" key={step.id}>
                  <span className="workflow-index">{step.id}</span>
                  <div>
                    <h3>{step.title}</h3>
                    <p>{step.body}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section section-engine" id="engine">
          <div className="section-heading">
            <p className="kicker">System View</p>
            <h2>Built like an operating layer, not a patchwork dashboard.</h2>
          </div>

          <div className="engine-layout">
            <div className="engine-copy">
              <p className="engine-statement">
                Planning, generation, queue state, and publishing feedback stay
                attached to the same campaign spine. That is what removes drift.
              </p>

              <div className="proof-list" role="list" aria-label="Core product capabilities">
                {proofPoints.map((point) => (
                  <div className="proof-item" key={point} role="listitem">
                    <span />
                    <p>{point}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="outcome-board">
              {outcomeRows.map((row) => (
                <div className="outcome-row" key={row.label}>
                  <strong>{row.metric}</strong>
                  <span>{row.label}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="section section-channels">
          <div className="section-heading">
            <p className="kicker">Channels</p>
            <h2>Facebook-first today. Multi-channel ready by design.</h2>
          </div>

          <div className="channel-list">
            {channelMatrix.map((channel) => (
              <article className="channel-row" key={channel.name}>
                <div>
                  <p className="channel-name">{channel.name}</p>
                  <p className="channel-detail">{channel.detail}</p>
                </div>
                <span className="channel-state">{channel.state}</span>
              </article>
            ))}
          </div>
        </section>

        <section className="section section-cta" id="launch">
          <div className="cta-frame">
            <p className="kicker">Launch</p>
            <h2>Stop assembling a stack. Start directing the flow.</h2>
            <p className="cta-copy">
              marektflow.ai is positioned for teams that want strategy,
              generation, and execution to move together. If that is the system
              you are building, the first impression should feel exactly like it.
            </p>

            <div className="cta-actions">
              <Link className="button button-primary" to="/register">
                Create workspace
              </Link>
              <a className="button button-secondary" href="#top">
                Back to top
              </a>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}
