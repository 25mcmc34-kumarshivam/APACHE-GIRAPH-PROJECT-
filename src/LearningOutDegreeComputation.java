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
import org.apache.giraph.graph.BasicComputation;
import org.apache.giraph.graph.Vertex;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.LongWritable;

/**
 * Calculates the out-degree of every vertex.
 *
 * <p>Out-degree means the number of directed edges leaving a vertex. Giraph
 * already stores each vertex's outgoing-edge list locally, so this algorithm
 * can count it immediately and does not need to exchange messages.</p>
 *
 * <p>The four generic types used by BasicComputation are:</p>
 * <ol>
 *   <li>LongWritable: vertex ID, for example 1 or 30.</li>
 *   <li>DoubleWritable: value stored at a vertex. We replace it with the
 *       calculated out-degree.</li>
 *   <li>FloatWritable: value/weight stored on each edge.</li>
 *   <li>DoubleWritable: possible message type. This algorithm sends no
 *       messages, but Giraph still requires a message type declaration.</li>
 * </ol>
 */
public class LearningOutDegreeComputation extends BasicComputation<
    LongWritable, DoubleWritable, FloatWritable, DoubleWritable> {

  /**
   * Runs once for every active vertex.
   *
   * @param vertex current vertex being processed by Giraph
   * @param messages messages delivered from the previous superstep; unused
   *     because out-degree is available from the local outgoing-edge list
   * @throws IOException if Giraph cannot read or write computation data
   */
  @Override
  public void compute(
      Vertex<LongWritable, DoubleWritable, FloatWritable> vertex,
      Iterable<DoubleWritable> messages) throws IOException {
    // Count entries in this vertex's outgoing-edge list.
    long outgoingEdgeCount = vertex.getNumEdges();

    // Save the answer as the vertex value.
    vertex.getValue().set(outgoingEdgeCount);

    // No messages or additional supersteps are needed.
    vertex.voteToHalt();
  }
}
