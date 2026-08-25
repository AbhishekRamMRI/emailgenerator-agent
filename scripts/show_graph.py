from emailgenerator_agent.agent.graph import email_graph

graph = email_graph.get_graph()

graph.draw_mermaid_png(output_file_path="email_graph.png")