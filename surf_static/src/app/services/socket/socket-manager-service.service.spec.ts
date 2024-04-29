import { TestBed } from '@angular/core/testing';

import { SocketManagerServiceService } from './socket-manager-service.service';

describe('SocketManagerServiceService', () => {
  let service: SocketManagerServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SocketManagerServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
