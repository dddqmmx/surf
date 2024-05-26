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

        // Use a smaller buffer size (512) for lower latency
        this.scriptProcessor = this.audioContext.createScriptProcessor(512, 1, 1);
        this.scriptProcessor.onaudioprocess = (event) => this.handleAudioProcess(event);

        const inputNode = this.audioContext.createMediaStreamSource(mediaStream);
        inputNode.connect(this.scriptProcessor);
        this.scriptProcessor.connect(this.audioContext.destination);

        this.audioChunks = [];
        this.isRecording = true;

        console.log('开始录制音频...');

        // Reduce the interval for data sending
        this.sendDataInterval = setInterval(() => {
          if (this.isRecording && this.audioChunks.length > 0) {
            this.sendAudioData();
          }
        }, 500); // Adjusted for lower latency
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
    // const regularArray = Array.from(message);
    // const jsonArray = JSON.stringify(regularArray);
    // console.log(jsonArray);

    this.playAudio(message);

    this.audioChunks = [];
  }

  playAudio(audioData: Float32Array) {
    if (!this.mainAudioContext) {
      this.mainAudioContext = new AudioContext();
    }

    this.mainAudioContext.resume();

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
}
