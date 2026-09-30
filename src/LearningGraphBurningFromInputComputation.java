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
import org.apache.giraph.conf.IntConfOption;
import org.apache.giraph.edge.Edge;
import org.apache.giraph.graph.BasicComputation;
import org.apache.giraph.graph.Vertex;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.LongWritable;

/**
 * Simulate Graph Burning using each vertex's input-file source round.
 *
 * <p>The input reader starts a scheduled source with a negative value, such
 * as -3 for a vertex selected in round 3. Zero means not selected. Once a
 * vertex burns, its value becomes its positive first-burn round. Thus the
 * source schedule stays with each vertex until it burns, and the input does
 * not require a separate colon-separated source list.</p>
 */
public class LearningGraphBurningFromInputComputation extends BasicComputation<
    LongWritable, DoubleWritable, FloatWritable, DoubleWritable> {
  /** Derived by the runner from the largest source round in the input. */
  public static final IntConfOption TOTAL_ROUNDS = new IntConfOption(
      "LearningGraphBurningFromInput.totalRounds", 1,
      "Number of graph-burning rounds scheduled in the input");

  @Override
  public void compute(
      Vertex<LongWritable, DoubleWritable, FloatWritable> vertex,
      Iterable<DoubleWritable> messages) throws IOException {
    int totalRounds = TOTAL_ROUNDS.get(getConf());
    if (totalRounds < 1) {
      throw new IllegalArgumentException("totalRounds must be positive");
    }

    long currentRound = getSuperstep() + 1;
    double storedValue = vertex.getValue().get();
    // A positive stored value is already the first burn round. A zero or
    // negative value means this vertex is still unburned.
    if (storedValue <= 0) {
      double firstArrival = Double.MAX_VALUE;
      for (DoubleWritable message : messages) {
        firstArrival = Math.min(firstArrival, message.get());
      }
      // -currentRound means this vertex was explicitly selected in the
      // input to ignite now. Fire and selection in the same round agree.
      if (storedValue == -currentRound) {
        firstArrival = Math.min(firstArrival, currentRound);
      }

      if (firstArrival != Double.MAX_VALUE) {
        vertex.getValue().set(firstArrival);
        // Giraph delivers these messages in the next superstep/round.
        if (currentRound < totalRounds) {
          for (Edge<LongWritable, FloatWritable> edge : vertex.getEdges()) {
            sendMessage(edge.getTargetVertexId(),
                new DoubleWritable(currentRound + 1));
          }
        }
      }
    }

    // Do not halt early: a future source may need to ignite without receiving
    // a message. After the final scheduled round every vertex can halt.
    if (currentRound >= totalRounds) {
      vertex.voteToHalt();
    }
  }
}
