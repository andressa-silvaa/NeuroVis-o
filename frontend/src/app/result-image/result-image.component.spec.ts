import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResultImageComponent } from './result-image.component';

describe('ResultImageComponent', () => {
  let component: ResultImageComponent;
  let fixture: ComponentFixture<ResultImageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResultImageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ResultImageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
