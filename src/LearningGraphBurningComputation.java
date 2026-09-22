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
import org.apache.giraph.conf.StrConfOption;
import org.apache.giraph.edge.Edge;
import org.apache.giraph.graph.BasicComputation;
import org.apache.giraph.graph.Vertex;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.LongWritable;

/**
 * Simulate deterministic graph burning for a supplied source sequence.
 *
 * <p>One new source is ignited in every round. A newly burned vertex spreads
 * fire to all outgoing neighbours for the next round. The final vertex value
 * is its first burn round, numbered from 1. An unburned vertex retains
 * {@link Double#MAX_VALUE}.</p>
 *
 * <p>This class evaluates a sequence; it does not claim to find the minimum
 * burning number. Example option:</p>
 *
 * <pre>
 * -ca LearningGraphBurning.sourceSequence=3:8:6
 * </pre>
 */
public class LearningGraphBurningComputation extends BasicComputation<
    LongWritable, DoubleWritable, FloatWritable, DoubleWritable> {

  /** Colon-separated vertex IDs, one source for each burning round. */
  public static final StrConfOption SOURCE_SEQUENCE = new StrConfOption(
      "LearningGraphBurning.sourceSequence", "1",
      "Colon-separated graph-burning source sequence");

  /**
   * Convert the configured colon-separated sequence into numeric vertex IDs.
   *
   * @return Ordered source vertex IDs
   */
  private long[] getSources() {
    String configured = SOURCE_SEQUENCE.get(getConf()).trim();
    if (configured.isEmpty()) {
      throw new IllegalArgumentException(
          "LearningGraphBurning.sourceSequence cannot be empty");
    }

    String[] tokens = configured.split(":");
    long[] sources = new long[tokens.length];
    for (int index = 0; index < tokens.length; index++) {
      sources[index] = Long.parseLong(tokens[index].trim());
    }
    return sources;
  }

  @Override
  public void compute(
      Vertex<LongWritable, DoubleWritable, FloatWritable> vertex,
      Iterable<DoubleWritable> messages) throws IOException {
    long[] sources = getSources();
    long superstep = getSuperstep();
    long currentRound = superstep + 1;

    if (superstep == 0) {
      // Infinity is the marker for a vertex that has not burned.
      vertex.getValue().set(Double.MAX_VALUE);
    }

    double earliestRound = vertex.getValue().get();

    // Fire messages were sent by vertices that burned in the previous round.
    for (DoubleWritable message : messages) {
      earliestRound = Math.min(earliestRound, message.get());
    }

    // Exactly one scheduled source is ignited during each configured round.
    if (superstep < sources.length &&
        vertex.getId().get() == sources[(int) superstep]) {
      earliestRound = Math.min(earliestRound, currentRound);
    }

    boolean newlyBurned = earliestRound < vertex.getValue().get();
    if (newlyBurned) {
      vertex.getValue().set(earliestRound);

      // A sequence of k sources defines exactly k rounds. Do not spread fire
      // into an extra round after the last source has been selected.
      if (earliestRound < sources.length) {
        double nextRound = earliestRound + 1;
        for (Edge<LongWritable, FloatWritable> edge : vertex.getEdges()) {
          sendMessage(
              edge.getTargetVertexId(), new DoubleWritable(nextRound));
        }
      }
    }

    // All vertices must remain active while future scheduled sources are due.
    // After the final round, no later message is needed and they may halt.
    if (currentRound >= sources.length) {
      vertex.voteToHalt();
    }
  }
}
