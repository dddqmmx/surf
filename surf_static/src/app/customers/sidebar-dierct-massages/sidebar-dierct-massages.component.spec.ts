import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SidebarDierctMassagesComponent } from './sidebar-dierct-massages.component';

describe('SidebarDierctMassagesComponent', () => {
  let component: SidebarDierctMassagesComponent;
  let fixture: ComponentFixture<SidebarDierctMassagesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SidebarDierctMassagesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SidebarDierctMassagesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
