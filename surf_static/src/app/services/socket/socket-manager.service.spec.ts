import { TestBed } from '@angular/core/testing';

import { SocketManagerService } from './socket-manager.service';

describe('SocketManagerServiceService', () => {
  let service: SocketManagerService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SocketManagerService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
