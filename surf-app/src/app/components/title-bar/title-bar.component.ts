import {Component} from '@angular/core';
import {getCurrentWindow} from "@tauri-apps/api/window";

@Component({
    selector: 'app-title-bar',
    standalone: true,
    imports: [],
    templateUrl: './title-bar.component.html',
    styleUrl: './title-bar.component.css'
})
export class TitleBarComponent {
    appWindow = getCurrentWindow();

    minimizeWindow() {
        this.appWindow.minimize();
    }

    maximizeWindow() {
        this.appWindow.toggleMaximize()
    }

    closeWindow() {
        this.appWindow.close()
    }
}
