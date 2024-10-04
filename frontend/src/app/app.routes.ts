import { Routes } from '@angular/router';
import { UploadImageComponent } from './upload-image/upload-image.component';

export const routes: Routes = [
  { path: 'upload', component: UploadImageComponent },
  { path: '', redirectTo: '/upload', pathMatch: 'full' },
];
