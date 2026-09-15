/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.giraph.examples;

import java.io.IOException;
import org.apache.giraph.edge.Edge;
import org.apache.giraph.graph.BasicComputation;
import org.apache.giraph.graph.Vertex;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.LongWritable;

/**
 * Calculates the in-degree of every vertex using Giraph message passing.
 *
 * <p>In-degree is the number of directed edges entering a vertex. A Giraph
 * vertex directly owns only its outgoing edges. In superstep 0 every vertex
 * sends one message along each outgoing edge. In superstep 1 each destination
 * counts its messages. One message represents one incoming edge.</p>
 *
 * <p>Generic types: LongWritable vertex ID, DoubleWritable vertex value,
 * FloatWritable edge weight, and DoubleWritable message value.</p>
 */
public class LearningInDegreeComputation extends BasicComputation<
    LongWritable, DoubleWritable, FloatWritable, DoubleWritable> {

  /**
   * Executes the send phase in superstep 0 and count phase in superstep 1.
   *
   * @param vertex current vertex
   * @param messages values sent to this vertex in the previous superstep
   * @throws IOException if Giraph cannot process computation data
   */
  @Override
  public void compute(
      Vertex<LongWritable, DoubleWritable, FloatWritable> vertex,
      Iterable<DoubleWritable> messages) throws IOException {
    if (getSuperstep() == 0) {
      // Send one marker to the destination of every outgoing edge.
      for (Edge<LongWritable, FloatWritable> outgoingEdge :
          vertex.getEdges()) {
        sendMessage(
            outgoingEdge.getTargetVertexId(), new DoubleWritable(1.0));
      }
      // Giraph continues because messages are waiting for superstep 1.
    } else {
      long incomingEdgeCount = 0;

      // One received marker equals one edge pointing to this vertex.
      for (DoubleWritable ignoredMessage : messages) {
        incomingEdgeCount++;
      }

      // Replace the initial vertex value with the calculated in-degree.
      vertex.getValue().set(incomingEdgeCount);
      vertex.voteToHalt();
    }
  }
}
