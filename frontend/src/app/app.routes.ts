import { Routes } from '@angular/router';
import { UploadImageComponent } from './upload-image/upload-image.component';
import { ModalComponent } from './modal/modal.component';
import { LoginComponent } from './login/login.component';
import { SignUpComponent } from './sign-up/sign-up.component';
import { ResultImageComponent } from './result-image/result-image.component';
import { AuthGuard } from './guards/auth.guard'; 

export const routes: Routes = [
  { path: 'upload-image', component: UploadImageComponent, canActivate: [AuthGuard] }, 
  { path: 'modal', component: ModalComponent, canActivate: [AuthGuard] }, 
  { path: 'result-image', component: ResultImageComponent, canActivate: [AuthGuard] }, 
  { path: 'login', component: LoginComponent },
  { path: 'sign-up', component: SignUpComponent }, 
  { path: '', redirectTo: '/login', pathMatch: 'full' }, 
  { path: '**', redirectTo: '/login' }
];