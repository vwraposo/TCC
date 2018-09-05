-- Creating first tables
CREATE TABLE snakes (
  sn_sp varchar(100) not NULL, 
  sn_ge varchar(100) not NULL,
  CONSTRAINT pk_sn PRIMARY KEY (sn_sp)
);

CREATE TABLE genes(
  gn_acc varchar(100) not NULL, 
  gn_desc text, 
  gn_seq text, 
  gn_alias varchar(100), 
  sn_sp varchar(100), 
  CONSTRAINT pk_gn PRIMARY KEY (gn_acc), 
  CONSTRAINT fk_sn FOREIGN KEY (sn_sp)
    REFERENCES snakes(sn_sp)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT alias UNIQUE (sn_sp, gn_alias)
);

-- Inserting snakes
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('moojeni', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('jararacussu', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('neuwiedi', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('erythromelas', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('insularis', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('jararaca', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('cotiara', 'Bothrops');
INSERT INTO snakes(sn_sp, sn_ge) VALUES ('atrox', 'Bothrops');


-- Creating Protein and Peptide:

CREATE TABLE peptides (
  pep_id serial,
  pep_seq varchar(100) not NULL, 
  CONSTRAINT pk_pep PRIMARY KEY (pep_id),
  CONSTRAINT sk_pep UNIQUE (pep_seq)
);

CREATE TABLE proteins (
  pr_acc varchar(100), 
  pr_toxclass varchar(100), 
  pr_T integer DEFAULT 0, 
  pr_WGA integer DEFAULT 0, 
  pr_ConA integer DEFAULT 0, 
  pr_PNA integer DEFAULT 0, 
  CONSTRAINT pk_pr PRIMARY KEY (pr_acc)
);

CREATE TABLE pep_pr (
  pep_id integer, 
  pr_acc varchar(100),
  CONSTRAINT fk_pr FOREIGN KEY (pr_acc)
    REFERENCES proteins(pr_acc)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_pep FOREIGN KEY (pep_id)
    REFERENCES peptides(pep_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT pk_pep_pr UNIQUE (pr_acc, pep_id)
);

CREATE TABlE pr_sn (
  sn_sp varchar(100), 
  pr_acc varchar(100),
  CONSTRAINT fk_pr FOREIGN KEY (pr_acc)
    REFERENCES proteins(pr_acc)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_sn FOREIGN KEY (sn_sp)
    REFERENCES snakes(sn_sp)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT pk_pr_sn UNIQUE (pr_acc, sn_sp)
);

CREATE TABLE pep_sn (
  pep_id integer, 
  sn_sp varchar(100),
  CONSTRAINT fk_sn FOREIGN KEY (sn_sp)
    REFERENCES snakes(sn_sp)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_pep FOREIGN KEY (pep_id)
    REFERENCES peptides(pep_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT pk_pep_sn UNIQUE (pep_id, sn_sp)
);

-- Creating N-glycan table

CREATE TABLE glycans (
  gl_id varchar(5), 
  CONSTRAINT pk_gl PRIMARY KEY (gl_id)
);

CREATE TABLE gl_sn (
  gl_id varchar(5), 
  sn_sp varchar(100),
  CONSTRAINT fk_sn FOREIGN KEY (sn_sp)
    REFERENCES snakes(sn_sp)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_gl FOREIGN KEY (gl_id)
    REFERENCES glycans(gl_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT pk_gl_sn UNIQUE (gl_id, sn_sp)
);


-- Tables for geologic and eating habits data 

CREATE TABLE geography (
  sn_sp varchar(100) not NULL, 
  CONSTRAINT fk_sn FOREIGN KEY (sn_sp)
    REFERENCES snakes(sn_sp)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  loc varchar(100),
  CONSTRAINT pk_geo UNIQUE (loc, sn_sp)
);

CREATE TABLE eating (
  sn_sp varchar(100), 
  CONSTRAINT fk_sn FOREIGN KEY (sn_sp)
    REFERENCES snakes(sn_sp)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  N integer, 
  centipedes real, 
  anurans real, 
  lizards real, 
  snakes real, 
  birds real, 
  mammals real,
  CONSTRAINT pk_eat PRIMARY KEY (sn_sp)
);


