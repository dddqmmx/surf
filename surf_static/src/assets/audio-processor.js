class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.buffer = [];
    this.bufferMaxSize = 1024;
    this.missedPackets = 0;
    this.excessPackets = 0;
    this.adjustmentThreshold = 5;
    this.minBufferSize = 5;
    this.maxBufferSize = 512;
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    const output = outputs[0];

    if (input.length > 0) {
      const inputChannel = input[0];
      this.buffer.push(new Float32Array(inputChannel));

      if (this.buffer.length >= this.bufferMaxSize) {
        const mergedBuffer = this.mergeBuffers(this.buffer);
        this.port.postMessage(mergedBuffer);
        this.buffer = [];
        this.excessPackets++;
        this.missedPackets = 0;
      } else if (this.buffer.length < this.bufferMaxSize / 2) {
        this.missedPackets++;
        this.excessPackets = 0;
      } else {
        this.missedPackets = 0;
        this.excessPackets = 0;
      }

      this.adjustBufferSize();
    }

    return true;
  }

  mergeBuffers(buffers) {
    let totalLength = buffers.reduce((sum, buf) => sum + buf.length, 0);
    let result = new Float32Array(totalLength);
    let offset = 0;
    for (let buffer of buffers) {
      result.set(buffer, offset);
      offset += buffer.length;
    }
    return result;
  }

  adjustBufferSize() {
    if (this.missedPackets > this.adjustmentThreshold) {
      this.increaseBufferSize();
    } else if (this.excessPackets > this.adjustmentThreshold) {
      this.decreaseBufferSize();
    }
  }

  increaseBufferSize() {
    this.bufferMaxSize = Math.min(this.bufferMaxSize * 2, this.maxBufferSize); // Adjust by doubling
    console.log(`Increased buffer size to: ${this.bufferMaxSize}`);
    this.missedPackets = 0;
  }

  decreaseBufferSize() {
    this.bufferMaxSize = Math.max(Math.floor(this.bufferMaxSize / 2), this.minBufferSize); // Adjust by halving
    console.log(`Decreased buffer size to: ${this.bufferMaxSize}`);
    this.excessPackets = 0;
  }
}

registerProcessor('audio-processor', AudioProcessor);
