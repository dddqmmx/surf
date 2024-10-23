import { Component } from '@angular/core';
import {appDataDir} from "@tauri-apps/api/path";
import {invoke} from "@tauri-apps/api/core";

@Component({
  selector: 'app-main',
  standalone: true,
  imports: [],
  templateUrl: './main.component.html',
  styleUrl: './main.component.css'
})
export class MainComponent {

}
