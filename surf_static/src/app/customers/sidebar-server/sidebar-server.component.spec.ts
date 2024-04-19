import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SidebarServerComponent } from './sidebar-server.component';

describe('SidebarChannelComponent', () => {
  let component: SidebarServerComponent;
  let fixture: ComponentFixture<SidebarServerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SidebarServerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SidebarServerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
