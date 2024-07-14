import { Injectable } from '@angular/core';
import {LocalDataService} from "../local_data/local-data.service";

@Injectable({
  providedIn: 'root'
})
export class VoiceChatService {
    constructor(private localDataService:LocalDataService) { }

    private audioContext: AudioContext | null = null;
    private mediaStream: MediaStream | null = null;
    private workletNode: AudioWorkletNode | null = null;
    private playbackAudioContext: AudioContext | null = null;
    isRecording: boolean = false;
    private playQueue: Float32Array[] = [];
    private isAudioContextInitialized: boolean = false;
    errorMessage: string = '';
    private playQueueMaxSize: number = 20; // 默认值
    private missedPackets: number = 0;
    private excessPackets: number = 0;
    private adjustmentThreshold: number = 5; // 调整阈值
    private minQueueSize: number = 10;
    private maxQueueSize: number = 50;
    private debug = true;

    private async initializeAudioContext() {
      if (!this.isAudioContextInitialized) {
        this.audioContext = new AudioContext();
        this.playbackAudioContext = new AudioContext();
        try {
          await this.audioContext.audioWorklet.addModule('/assets/audio-processor.js');
          this.isAudioContextInitialized = true;
        } catch (error) {
          console.error('无法加载 audio-processor.js:', error);
          this.errorMessage = '无法初始化音频处理器。请刷新页面重试。';
          throw error;
        }
      }
    }

    async startRecording(serverId:string,channelId:string) {
        this.localDataService.voiceCallServerName = this.localDataService.getServerById(serverId)?.name
        this.localDataService.voiceCallChannelName = this.localDataService.getChannelById(channelId)?.name

      if (this.localDataService.isInVoiceCall) return;

      this.errorMessage = ''; // 清除之前的错误消息

      try {
        await this.initializeAudioContext();

        if (this.audioContext?.state === 'suspended') {
          await this.audioContext.resume();
        }

        if (this.playbackAudioContext?.state === 'suspended') {
          await this.playbackAudioContext.resume();
        }

        this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const source = this.audioContext!.createMediaStreamSource(this.mediaStream);

        this.workletNode = new AudioWorkletNode(this.audioContext!, 'audio-processor');
        this.workletNode.port.onmessage = (event) => {
          this.handleAudioData(event.data);
        };

        source.connect(this.workletNode);
        this.workletNode.connect(this.audioContext!.destination);

        this.localDataService.isInVoiceCall = true;
      } catch (err) {
        console.error('无法开始录音:', err);
        if (err instanceof DOMException) {
          if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            this.errorMessage = '麦克风访问被拒绝。请检查您的浏览器设置并允许麦克风访问。';
          } else if (err.name === 'NotFoundError') {
            this.errorMessage = '未找到麦克风设备。请确保您的设备已正确连接。';
          } else if (err.name === 'AbortError') {
            this.errorMessage = '录音请求被中断。请重试。';
          } else {
            this.errorMessage = '录音过程中发生错误。请重试。';
          }
        } else {
          this.errorMessage = '发生未知错误。请重试。';
        }
      }
    }

    stopRecording() {
      if (!this.localDataService.isInVoiceCall) return;

      this.localDataService.isInVoiceCall = false;
      if (this.workletNode) {
        this.workletNode.disconnect();
        this.workletNode = null;
      }
      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach((track) => track.stop());
        this.mediaStream = null;
      }
    }

    private handleAudioData(audioData: Float32Array) {
      this.playQueue.push(audioData);

      if (this.playQueue.length > this.playQueueMaxSize) {
        this.playQueue.shift();
        this.excessPackets++;
        this.missedPackets = 0;
      } else if (this.playQueue.length < this.playQueueMaxSize / 2) {
        this.missedPackets++;
        this.excessPackets = 0;
      } else {
        this.missedPackets = 0;
        this.excessPackets = 0;
      }
      this.adjustQueueSize();

      if (this.debug){
          this.playBufferedAudio();
      }
    }

    private adjustQueueSize() {
      if (this.missedPackets > this.adjustmentThreshold) {
        this.increaseQueueSize();
      } else if (this.excessPackets > this.adjustmentThreshold) {
        this.decreaseQueueSize();
      }
    }

    private increaseQueueSize() {
      this.playQueueMaxSize = Math.min(this.playQueueMaxSize + 5, this.maxQueueSize);
      console.log(`增加队列大小到: ${this.playQueueMaxSize}`);
      this.missedPackets = 0;
    }

    private decreaseQueueSize() {
      this.playQueueMaxSize = Math.max(this.playQueueMaxSize - 5, this.minQueueSize);
      console.log(`减小队列大小到: ${this.playQueueMaxSize}`);
      this.excessPackets = 0;
    }

    private async playBufferedAudio() {
      if (!this.playbackAudioContext) return;

      if (this.playbackAudioContext.state === 'suspended') {
        try {
          await this.playbackAudioContext.resume();
        } catch (err) {
          console.error('无法恢复播放上下文:', err);
          this.errorMessage = '无法开始音频播放。请重试。';
          return;
        }
      }

      while (this.playQueue.length > 0) {
        const audioData = this.playQueue.shift();
        if (audioData) {
          const audioBuffer = this.playbackAudioContext.createBuffer(1, audioData.length, this.playbackAudioContext.sampleRate);
          audioBuffer.getChannelData(0).set(audioData);

          const source = this.playbackAudioContext.createBufferSource();
          source.buffer = audioBuffer;
          source.connect(this.playbackAudioContext.destination);
          source.start();

          await new Promise(resolve => {
            source.onended = resolve;
          });
        }
      }
    }
}
