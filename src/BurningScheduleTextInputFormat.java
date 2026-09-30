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
import java.util.ArrayList;
import java.util.List;
import org.apache.giraph.conf.ImmutableClassesGiraphConfigurable;
import org.apache.giraph.conf.ImmutableClassesGiraphConfiguration;
import org.apache.giraph.edge.Edge;
import org.apache.giraph.edge.EdgeFactory;
import org.apache.giraph.graph.Vertex;
import org.apache.giraph.io.formats.TextVertexInputFormat;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.mapreduce.InputSplit;
import org.apache.hadoop.mapreduce.TaskAttemptContext;

/**
 * Read "vertexId sourceRound neighborId:weight ..." for Graph Burning.
 *
 * <p>sourceRound is 0 for an ordinary vertex, or 1, 2, ... for a scheduled
 * ignition. We initially store -sourceRound in the vertex value, so it stays
 * available until this vertex first burns. A positive value later represents
 * the first burn round. Zero means an unscheduled, still-unburned vertex.</p>
 */
public class BurningScheduleTextInputFormat extends TextVertexInputFormat<
    LongWritable, DoubleWritable, FloatWritable> implements
    ImmutableClassesGiraphConfigurable<
        LongWritable, DoubleWritable, FloatWritable> {
  private ImmutableClassesGiraphConfiguration<
      LongWritable, DoubleWritable, FloatWritable> configuration;

  @Override
  public void setConf(ImmutableClassesGiraphConfiguration<
      LongWritable, DoubleWritable, FloatWritable> conf) {
    configuration = conf;
  }

  @Override
  public ImmutableClassesGiraphConfiguration<
      LongWritable, DoubleWritable, FloatWritable> getConf() {
    return configuration;
  }

  @Override
  public TextVertexReader createVertexReader(
      InputSplit split, TaskAttemptContext context) throws IOException {
    return new BurningScheduleVertexReader();
  }

  /** Convert one text record to a Giraph vertex. */
  public class BurningScheduleVertexReader extends TextVertexReader {
    @Override
    public Vertex<LongWritable, DoubleWritable, FloatWritable>
        getCurrentVertex() throws IOException, InterruptedException {
      String line = getRecordReader().getCurrentValue().toString().trim();
      String[] tokens = line.split("\\s+");
      if (tokens.length < 2) {
        throw new IllegalArgumentException(
            "Expected vertexId sourceRound [neighbor:weight ...]: " + line);
      }

      long vertexId = Long.parseLong(tokens[0]);
      int sourceRound = Integer.parseInt(tokens[1]);
      if (sourceRound < 0) {
        throw new IllegalArgumentException(
            "sourceRound must be 0 or positive: " + line);
      }

      List<Edge<LongWritable, FloatWritable>> edges =
          new ArrayList<Edge<LongWritable, FloatWritable>>();
      for (int index = 2; index < tokens.length; index++) {
        String[] parts = tokens[index].split(":", -1);
        if (parts.length != 2) {
          throw new IllegalArgumentException(
              "Expected neighborId:weight in: " + line);
        }
        edges.add(EdgeFactory.create(
            new LongWritable(Long.parseLong(parts[0])),
            new FloatWritable(Float.parseFloat(parts[1]))));
      }

      Vertex<LongWritable, DoubleWritable, FloatWritable> vertex =
          configuration.createVertex();
      vertex.initialize(
          new LongWritable(vertexId),
          new DoubleWritable(-sourceRound), edges);
      return vertex;
    }

    @Override
    public boolean nextVertex() throws IOException, InterruptedException {
      return getRecordReader().nextKeyValue();
    }
  }
}
