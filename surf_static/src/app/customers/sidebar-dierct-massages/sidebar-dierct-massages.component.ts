import { Component } from '@angular/core';
import {NgForOf} from "@angular/common";

@Component({
  selector: 'app-sidebar-dierct-massages',
  standalone: true,
    imports: [
        NgForOf
    ],
  templateUrl: './sidebar-dierct-massages.component.html',
  styleUrl: './sidebar-dierct-massages.component.css'
})
export class SidebarDierctMassagesComponent {
    userList =  [
        { name: "白上フブキ"},
        { name: "桐生一馬"},
        { name: "小島秀夫"},
        { name: "大空スバル" },
        { name: "日南" },
        { name: "みけねこ" }
    ]
}
