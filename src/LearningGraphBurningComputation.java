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
  // Types above, in order: vertex ID, value stored at a vertex, edge value,
  // and message value. The input reader uses long IDs, double vertex values,
  // and float edge weights; our fire messages also carry double values.

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
    // Giraph passes -ca KEY=VALUE settings to every worker. This reads the
    // ordered source IDs, for example "3:8:6" for three burning rounds.
    String configured = SOURCE_SEQUENCE.get(getConf()).trim();
    if (configured.isEmpty()) {
      throw new IllegalArgumentException(
          "LearningGraphBurning.sourceSequence cannot be empty");
    }

    // A colon is used because Giraph treats commas inside -ca as separators
    // between DIFFERENT configuration settings.
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
    // Giraph calls compute once per active vertex in each superstep.
    // Each vertex gets only its own state and messages sent to it; it does
    // not directly read all other vertices as a single local program would.
    long[] sources = getSources();
    // Computer supersteps start at 0; our human burning rounds start at 1.
    long superstep = getSuperstep();
    long currentRound = superstep + 1;

    if (superstep == 0) {
      // Initialize every vertex to "not burned" at the start of the job.
      // Double.MAX_VALUE is only a marker, not a real number of rounds.
      vertex.getValue().set(Double.MAX_VALUE);
    }

    double earliestRound = vertex.getValue().get();

    // The vertex's stored value is its first known burn round. Messages
    // arriving now came from neighbours burned in the previous round.
    // Math.min keeps the earliest arrival if several neighbours send fire.
    for (DoubleWritable message : messages) {
      earliestRound = Math.min(earliestRound, message.get());
    }

    // Source number 0 is ignited in round 1, source number 1 in round 2, etc.
    // This checks whether THIS vertex is the chosen source for this round.
    if (superstep < sources.length &&
        vertex.getId().get() == sources[(int) superstep]) {
      earliestRound = Math.min(earliestRound, currentRound);
    }

    // An unchanged value means the vertex was already burned earlier (or is
    // still unburned), so it must not repeat its outgoing messages.
    boolean newlyBurned = earliestRound < vertex.getValue().get();
    if (newlyBurned) {
      vertex.getValue().set(earliestRound);

      // A sequence of k sources defines exactly k rounds. A vertex burned
      // in round r sends (r+1) to neighbours; Giraph delivers it in the next
      // superstep. Do not create a message for round k+1.
      if (earliestRound < sources.length) {
        double nextRound = earliestRound + 1;
        for (Edge<LongWritable, FloatWritable> edge : vertex.getEdges()) {
          sendMessage(
              edge.getTargetVertexId(), new DoubleWritable(nextRound));
        }
      }
    }

    // A future source might receive no message, but it must still execute
    // when its scheduled round arrives. Therefore vertices do not halt early.
    // At the end of the final configured round, every vertex may halt.
    if (currentRound >= sources.length) {
      vertex.voteToHalt();
    }
  }
}
