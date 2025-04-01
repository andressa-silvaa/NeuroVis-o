import { Routes } from '@angular/router';
import { UploadImageComponent } from './upload-image/upload-image.component';
import { ModalComponent } from './modal/modal.component';
import { LoginComponent } from './login/login.component';
import { SignUpComponent } from './sign-up/sign-up.component';

export const routes: Routes = [
  { path: 'upload', component: UploadImageComponent },
  { path:'modal', component: ModalComponent},
  { path:'login', component: LoginComponent},
  { path:'sign-up', component: SignUpComponent},
  { path: '', redirectTo: '/sign-up', pathMatch: 'full' },
];
