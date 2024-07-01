import { Component } from '@angular/core';

@Component({
  selector: 'app-hello',
  standalone: true,
  imports: [],
  templateUrl: './hello.component.html',
  styleUrl: './hello.component.css'
})
export class HelloComponent {
  mediaStream: MediaStream | null = null;
  audioContext: AudioContext | null = null;
  scriptProcessor: ScriptProcessorNode | null = null;
  audioChunks: Float32Array[] = [];
  isRecording: boolean = false;
  sendDataInterval: any;
  mainAudioContext: AudioContext | null = null;
  playQueue: Float32Array[] = [];
  bufferSize: number = 4096; // Fixed buffer size for audio processing (adjust as needed)
  maxQueueSize: number = 500; // Fixed max queue size (adjust as needed)
  messageTimestamps: number[] = []; // Array to store message timestamps
  adjustmentInterval: number = 5000; // Interval to adjust parameters (in milliseconds)
  minSendDataInterval: number = 50; // Minimum interval for sendDataInterval (adjust as needed)
  maxSendDataInterval: number = 500; // Maximum interval for sendDataInterval (adjust as needed)

  async startRecording() {
    if (this.isRecording) {
      console.log('已经在录制中...');
      return;
    }
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      if (mediaStream.active) {
        console.log('音频流已经开始传输。');

        this.mediaStream = mediaStream;
        this.audioContext = new AudioContext();

        this.scriptProcessor = this.audioContext.createScriptProcessor(this.bufferSize, 1, 1);
        this.scriptProcessor.onaudioprocess = (event) => this.handleAudioProcess(event);

        const inputNode = this.audioContext.createMediaStreamSource(mediaStream);
        inputNode.connect(this.scriptProcessor);
        this.scriptProcessor.connect(this.audioContext.destination);

        this.audioChunks = [];
        this.isRecording = true;

        console.log('开始录制音频...');

        this.sendDataInterval = setInterval(() => {
          if (this.isRecording && this.audioChunks.length > 0) {
            this.sendAudioData();
          }
        }, this.maxSendDataInterval); // Use the maximum interval for sendDataInterval

        // Start adjusting parameters periodically
        setInterval(() => this.adjustParameters(), this.adjustmentInterval);
      }
    } catch (err) {
      console.error('无法访问麦克风:', err);
    }
  }

  handleAudioProcess(event: AudioProcessingEvent) {
    if (!this.isRecording) return;

    const audioBuffer = event.inputBuffer;
    const inputData = new Float32Array(audioBuffer.getChannelData(0));
    this.audioChunks.push(inputData);
  }

  stopRecording() {
    if (!this.isRecording) {
      console.log('未在录制中...');
      return;
    }

    this.isRecording = false;
    clearInterval(this.sendDataInterval);

    if (this.scriptProcessor) {
      this.scriptProcessor.disconnect();
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
    }
    if (this.audioContext) {
      this.audioContext.close();
    }

    console.log('停止录制音频...');
    this.sendAudioData();
  }

  sendAudioData() {
    if (this.audioChunks.length === 0) {
      console.log('没有录制的音频数据...');
      return;
    }

    const message = this.mergeArrays(this.audioChunks);
    this.audioChunks = [];

    // Record the timestamp of the message
    this.messageTimestamps.push(Date.now());

    // Append new data to the play queue
    this.playQueue.push(message);

    // Keep the play queue within the max size
    while (this.playQueue.length > this.maxQueueSize) {
      console.log("playQueue.shift() to maintain maxQueueSize")
      this.playQueue.shift();
    }

    // Play audio if enough data is buffered
    if (this.playQueue.length > 0) {
      this.playBufferedAudio();
    }
  }

  async playBufferedAudio() {
    if (!this.mainAudioContext) {
      this.mainAudioContext = new AudioContext();
    }

    while (this.playQueue.length > 0) {
      const audioData = this.playQueue.shift();
      if (audioData) {
        const channelCount = 1;
        const sampleRate = this.mainAudioContext.sampleRate;
        const totalSamples = audioData.length;

        const audioBuffer = this.mainAudioContext.createBuffer(channelCount, totalSamples, sampleRate);
        const channelData = audioBuffer.getChannelData(0);

        channelData.set(audioData);

        const source = this.mainAudioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(this.mainAudioContext.destination);
        source.start();

        // Wait for the audio to finish playing before proceeding
        await new Promise(resolve => {
          source.onended = resolve;
        });
      }
    }
  }

  mergeArrays(arrays: Float32Array[]): Float32Array {
    let totalLength = arrays.reduce((sum, array) => sum + array.length, 0);
    let result = new Float32Array(totalLength);
    let offset = 0;

    arrays.forEach((array) => {
      result.set(array, offset);
      offset += array.length;
    });

    return result;
  }

  adjustParameters() {
    const now = Date.now();
    // Remove timestamps older than the adjustment interval
    this.messageTimestamps = this.messageTimestamps.filter(timestamp => now - timestamp <= this.adjustmentInterval);

    // Calculate the message rate (messages per second)
    const messageRate = this.messageTimestamps.length / (this.adjustmentInterval / 1000);

    // Log current parameters for reference
    console.log(`当前参数设置: bufferSize=${this.bufferSize}, maxQueueSize=${this.maxQueueSize}, maxSendDataInterval=${this.maxSendDataInterval}`);

    // Example adjustments (you can customize this logic)
    // For simplicity, let's keep the parameters fixed
    // You can implement more sophisticated logic based on your requirements
    // this.bufferSize = calculateOptimalBufferSize(messageRate);
    // this.maxQueueSize = calculateOptimalMaxQueueSize(messageRate);
    // this.maxSendDataInterval = calculateOptimalSendDataInterval(messageRate);

    console.log(`调整后的参数设置: bufferSize=${this.bufferSize}, maxQueueSize=${this.maxQueueSize}, maxSendDataInterval=${this.maxSendDataInterval}`);
  }
}
