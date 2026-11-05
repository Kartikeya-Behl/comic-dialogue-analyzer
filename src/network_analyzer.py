"""
Conversational Social Network Graph and Centrality Metrics Analyzer.
Builds directed conversational networks of who addresses whom,
computes network centrality metrics (Degree, Betweenness, In/Out-Degree),
and creates interactive Plotly network visualizations.
"""

import math
from typing import Dict, List, Optional, Tuple, Any
from .character_popularity import CharacterPopularityEngine, CharacterStats


class ConversationalNetworkAnalyzer:
    """
    Constructs and analyzes the directed character interaction network.
    Edges represent Character A addressing Character B via vocative patterns.
    """

    def __init__(self, popularity_engine: CharacterPopularityEngine):
        self.engine = popularity_engine

    def build_network_data(
        self,
        min_score: float = 0.0,
        top_n: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Extracts nodes, directed edges, and centrality metrics from character registry.
        """
        rankings = self.engine.compute_rankings()
        if top_n is not None and top_n > 0:
            rankings = rankings[:top_n]
        if min_score > 0:
            rankings = [c for c in rankings if c.popularity_score >= min_score]

        selected_names = {c.canonical_name for c in rankings}

        # Build adjacency matrix / edge list
        edges: List[Dict[str, Any]] = []
        in_degrees: Dict[str, int] = {name: 0 for name in selected_names}
        out_degrees: Dict[str, int] = {name: 0 for name in selected_names}

        for c in rankings:
            spk = c.canonical_name
            for target, count in c.addressed_others.items():
                if target in selected_names:
                    edges.append({
                        "source": spk,
                        "target": target,
                        "weight": count
                    })
                    out_degrees[spk] = out_degrees.get(spk, 0) + count
                    in_degrees[target] = in_degrees.get(target, 0) + count

        # Compute NetworkX metrics if networkx is available
        betweenness_map: Dict[str, float] = {name: 0.0 for name in selected_names}
        degree_cent_map: Dict[str, float] = {name: 0.0 for name in selected_names}
        in_degree_cent_map: Dict[str, float] = {name: 0.0 for name in selected_names}
        out_degree_cent_map: Dict[str, float] = {name: 0.0 for name in selected_names}
        pagerank_map: Dict[str, float] = {name: 0.0 for name in selected_names}

        n_nodes = len(selected_names)
        norm_factor = max(1, n_nodes - 1)

        try:
            import networkx as nx
            G = nx.DiGraph()
            for name in selected_names:
                G.add_node(name)
            for edge in edges:
                G.add_edge(edge["source"], edge["target"], weight=edge["weight"])

            if n_nodes > 1:
                deg_c = nx.degree_centrality(G)
                in_deg_c = nx.in_degree_centrality(G)
                out_deg_c = nx.out_degree_centrality(G)
                bet_c = nx.betweenness_centrality(G, weight="weight")
                try:
                    pr = nx.pagerank(G, weight="weight")
                except Exception:
                    pr = {name: 1.0 / n_nodes for name in selected_names}

                degree_cent_map = {k: round(v, 4) for k, v in deg_c.items()}
                in_degree_cent_map = {k: round(v, 4) for k, v in in_deg_c.items()}
                out_degree_cent_map = {k: round(v, 4) for k, v in out_deg_c.items()}
                betweenness_map = {k: round(v, 4) for k, v in bet_c.items()}
                pagerank_map = {k: round(v, 4) for k, v in pr.items()}
        except ImportError:
            # Fallback native computation for degree centralities
            for name in selected_names:
                total_deg = in_degrees.get(name, 0) + out_degrees.get(name, 0)
                degree_cent_map[name] = round(total_deg / (2 * norm_factor), 4)
                in_degree_cent_map[name] = round(in_degrees.get(name, 0) / norm_factor, 4)
                out_degree_cent_map[name] = round(out_degrees.get(name, 0) / norm_factor, 4)

        # Compile node records
        node_records: List[Dict[str, Any]] = []
        for c in rankings:
            name = c.canonical_name
            node_records.append({
                "character": name,
                "score": round(c.popularity_score, 2),
                "spoken": c.spoken_count,
                "addressed": c.addressed_count,
                "mentioned": c.mentioned_count,
                "tone": c.tone_count,
                "in_degree": in_degrees.get(name, 0),
                "out_degree": out_degrees.get(name, 0),
                "total_degree": in_degrees.get(name, 0) + out_degrees.get(name, 0),
                "degree_centrality": degree_cent_map.get(name, 0.0),
                "in_degree_centrality": in_degree_cent_map.get(name, 0.0),
                "out_degree_centrality": out_degree_cent_map.get(name, 0.0),
                "betweenness_centrality": betweenness_map.get(name, 0.0),
                "pagerank": pagerank_map.get(name, 0.0)
            })

        return {
            "nodes": node_records,
            "edges": edges,
            "total_nodes": len(node_records),
            "total_edges": len(edges)
        }

    def generate_plotly_figure(
        self,
        top_n: int = 15,
        color_by: str = "in_degree_centrality",
        is_dark: bool = True
    ) -> Optional[Any]:
        """
        Creates an interactive Plotly Figure representing the character interaction network.
        Nodes are sized proportionally to popularity score and positioned with spring layout.
        """
        try:
            import plotly.graph_objects as go
            import networkx as nx
        except ImportError:
            return None

        net_data = self.build_network_data(top_n=top_n)
        nodes = net_data["nodes"]
        edges = net_data["edges"]

        if not nodes:
            return None

        # Build NetworkX DiGraph for layout calculation
        G = nx.DiGraph()
        for n in nodes:
            G.add_node(n["character"], **n)
        for e in edges:
            G.add_edge(e["source"], e["target"], weight=e["weight"])

        # Determine layout
        if len(nodes) <= 12:
            pos = nx.circular_layout(G)
        else:
            pos = nx.spring_layout(G, k=1.4 / math.sqrt(max(1, len(nodes))), seed=42, iterations=80)

        # Edges and Arrows
        edge_x = []
        edge_y = []
        edge_text = []
        annotations = []

        max_weight = max((e["weight"] for e in edges), default=1)
        arrow_color = 'rgba(148, 163, 184, 0.75)' if is_dark else 'rgba(100, 116, 139, 0.85)'
        edge_color = 'rgba(148, 163, 184, 0.45)' if is_dark else 'rgba(148, 163, 184, 0.65)'
        node_text_color = '#E2E8F0' if is_dark else '#0F172A'
        title_color = '#F8FAFC' if is_dark else '#0F172A'
        plot_bg = 'rgba(0, 0, 0, 0)' if is_dark else 'rgba(241, 245, 249, 0.6)'

        for e in edges:
            x0, y0 = pos[e["source"]]
            x1, y1 = pos[e["target"]]
            weight = e["weight"]

            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_text.append(f"{e['source']} → {e['target']} ({weight} interaction{'s' if weight > 1 else ''})")

            # Draw directional arrows on edges
            # Place arrow slightly before target node
            dx = x1 - x0
            dy = y1 - y0
            dist = math.hypot(dx, dy)
            if dist > 0.05:
                # Arrow position at 75% along the line
                ax = x0 + 0.75 * dx
                ay = y0 + 0.75 * dy
                arrow_width = max(1.0, min(4.5, 1.0 + 3.0 * (weight / max_weight)))
                annotations.append(dict(
                    ax=x0 + 0.60 * dx,
                    ay=y0 + 0.60 * dy,
                    x=ax,
                    y=ay,
                    xref='x',
                    yref='y',
                    axref='x',
                    ayref='y',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.2,
                    arrowwidth=arrow_width,
                    arrowcolor=arrow_color
                ))

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1.5, color=edge_color),
            hoverinfo='none',
            mode='lines'
        )

        # Node coordinates and sizing
        node_x = []
        node_y = []
        node_sizes = []
        node_colors = []
        node_hover = []
        node_labels = []

        max_score = max((n["score"] for n in nodes), default=1.0)
        min_score = min((n["score"] for n in nodes), default=0.0)
        score_range = max(1.0, max_score - min_score)

        for n in nodes:
            x, y = pos[n["character"]]
            node_x.append(x)
            node_y.append(y)

            # Node size scaled from 18px to 52px based on popularity score
            normalized_score = (n["score"] - min_score) / score_range
            radius = 18 + normalized_score * 34
            node_sizes.append(radius)

            # Color metric
            metric_val = n.get(color_by, n["score"])
            node_colors.append(metric_val)

            node_labels.append(n["character"])
            hover_html = (
                f"<b>{n['character']}</b><br>"
                f"Popularity Score: {n['score']:.1f} pts<br>"
                f"Lines Spoken: {n['spoken']}<br>"
                f"Addressed by Others (In-Degree): {n['in_degree']}<br>"
                f"Addresses Others (Out-Degree): {n['out_degree']}<br>"
                f"Degree Centrality: {n['degree_centrality']:.4f}<br>"
                f"Betweenness Centrality: {n['betweenness_centrality']:.4f}<br>"
                f"PageRank Prestige: {n['pagerank']:.4f}"
            )
            node_hover.append(hover_html)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=node_labels,
            textposition='top center',
            textfont=dict(size=12, family="sans-serif", color=node_text_color),
            hoverinfo='text',
            hovertext=node_hover,
            marker=dict(
                showscale=True,
                colorscale='Viridis',
                reversescale=True,
                color=node_colors,
                size=node_sizes,
                colorbar=dict(
                    thickness=14,
                    title=dict(
                        text=color_by.replace('_', ' ').title(),
                        side='right'
                    ),
                    xpad=5
                ),
                line=dict(width=2, color='#FFFFFF')
            )
        )

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=dict(
                    text=f"Conversational Interaction Network (Top {len(nodes)} Characters)",
                    font=dict(size=18, color=title_color)
                ),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=20, r=20, t=50),
                annotations=annotations,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor=plot_bg,
                paper_bgcolor='rgba(0, 0, 0, 0)',
                height=550
            )
        )
        return fig

    def render_text_network_summary(self, top_n: int = 10) -> str:
        """
        Renders an ASCII text summary of the network and top central characters for CLI reporting.
        """
        data = self.build_network_data(top_n=top_n)
        nodes = data["nodes"]
        edges = data["edges"]

        lines = []
        lines.append("=" * 80)
        lines.append("           CONVERSATIONAL SOCIAL NETWORK & CENTRALITY METRICS")
        lines.append("=" * 80)
        lines.append(f"Network Scope       : {data['total_nodes']} Characters, {data['total_edges']} Directed Conversational Edges")
        lines.append("-" * 80)
        lines.append(
            f"{'RANK':<5}{'CHARACTER':<18}{'IN-DEG':<8}{'OUT-DEG':<9}{'DEG-CENT':<11}{'BETWEENNESS':<13}{'SCORE':<8}"
        )
        lines.append("-" * 80)

        for i, n in enumerate(nodes[:top_n], 1):
            lines.append(
                f"{i:<5}{n['character']:<18}{n['in_degree']:<8}{n['out_degree']:<9}"
                f"{n['degree_centrality']:<11.3f}{n['betweenness_centrality']:<13.4f}{n['score']:<8.1f}"
            )

        if edges:
            lines.append("-" * 80)
            lines.append("TOP CONVERSATIONAL INTERACTION EDGES (WHO ADDRESSES WHOM):")
            sorted_edges = sorted(edges, key=lambda e: e["weight"], reverse=True)
            for e in sorted_edges[:8]:
                lines.append(f"  * {e['source']:<16} --({e['weight']:>2} times)--> {e['target']}")

        lines.append("=" * 80)
        return "\n".join(lines)
