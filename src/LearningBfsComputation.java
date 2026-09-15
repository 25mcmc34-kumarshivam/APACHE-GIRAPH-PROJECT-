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
import org.apache.giraph.conf.LongConfOption;
import org.apache.giraph.edge.Edge;
import org.apache.giraph.graph.BasicComputation;
import org.apache.giraph.graph.Vertex;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.LongWritable;

/**
 * Breadth-first search (BFS) from one configurable source vertex.
 *
 * <p>The stored value becomes the minimum number of directed edges (hops) from
 * the source. Edge weights are deliberately ignored: BFS is for an unweighted
 * graph. Use SimpleShortestPathsComputation when edge weights affect
 * distance.</p>
 */
public class LearningBfsComputation extends BasicComputation<
    LongWritable, DoubleWritable, FloatWritable, DoubleWritable> {

  /** Command-line setting: -ca LearningBfsComputation.sourceId=1 */
  public static final LongConfOption SOURCE_ID = new LongConfOption(
      "LearningBfsComputation.sourceId", 1L,
      "Vertex from which BFS starts");

  @Override
  public void compute(
      Vertex<LongWritable, DoubleWritable, FloatWritable> vertex,
      Iterable<DoubleWritable> messages) throws IOException {
    if (getSuperstep() == 0) {
      // Infinity means this vertex has not yet been reached.
      vertex.getValue().set(Double.MAX_VALUE);
    }

    // The source starts at zero. Other vertices obtain candidates from
    // messages that were sent during the previous superstep.
    double smallestCandidate =
        vertex.getId().get() == SOURCE_ID.get(getConf())
            ? 0.0 : Double.MAX_VALUE;

    for (DoubleWritable message : messages) {
      smallestCandidate = Math.min(smallestCandidate, message.get());
    }

    // Propagate only when this vertex discovers a shorter hop distance.
    if (smallestCandidate < vertex.getValue().get()) {
      vertex.getValue().set(smallestCandidate);
      double neighborDistance = smallestCandidate + 1.0;

      for (Edge<LongWritable, FloatWritable> outgoingEdge :
          vertex.getEdges()) {
        sendMessage(
            outgoingEdge.getTargetVertexId(),
            new DoubleWritable(neighborDistance));
      }
    }

    // A later message can reactivate the vertex if it provides a shorter path.
    vertex.voteToHalt();
  }
}
