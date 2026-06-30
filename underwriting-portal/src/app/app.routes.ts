import { Routes } from '@angular/router';
import { ApplicationSubmitComponent } from './pages/application-submit/application-submit.component';

export const routes: Routes = [
  { path: '', component: ApplicationSubmitComponent },
  { path: '**', redirectTo: '' },
];
