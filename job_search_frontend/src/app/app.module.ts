import { NgModule } from '@angular/core';
import { BrowserModule, provideClientHydration } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { JobListComponent } from './modules/job-list/job-list.component';
import { HTTP_INTERCEPTORS, HttpClientModule, provideHttpClient, withInterceptors } from '@angular/common/http';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner'
import { loaderInterceptor } from './interceptors/interceptor.service';

import { MatProgressBarModule } from "@angular/material/progress-bar";
import { FormsModule } from '@angular/forms';
import { NgSelectModule } from '@ng-select/ng-select';

import { NgbPaginationModule } from '@ng-bootstrap/ng-bootstrap';
import { MatBottomSheetModule } from '@angular/material/bottom-sheet';
import { MatListModule } from '@angular/material/list';
import { MatSidenavModule } from '@angular/material/sidenav';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    AppComponent,
    JobListComponent  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    MatProgressSpinnerModule,
    MatProgressBarModule,
    FormsModule,
    NgSelectModule,
    NgbPaginationModule,
    MatBottomSheetModule,
    MatListModule,
    MatSidenavModule,
    BrowserAnimationsModule

  ],
  providers: [
    provideHttpClient(withInterceptors([loaderInterceptor])),
    provideClientHydration(),
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
