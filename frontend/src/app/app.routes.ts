import { Routes } from '@angular/router';
import { UploadImageComponent } from './upload-image/upload-image.component';
import { ModalComponent } from './modal/modal.component';
export const routes: Routes = [
  { path: 'upload', component: UploadImageComponent },
  { path:'modal', component: ModalComponent},
  { path: '', redirectTo: '/upload', pathMatch: 'full' },
];
