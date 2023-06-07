--
-- Base de datos: bytebuilders
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla creditcards
--

DROP TABLE  IF EXISTS transactions;
DROP TABLE  IF EXISTS creditcards;
DROP TABLE  IF EXISTS users;

CREATE TABLE creditcards (
  card_id integer NOT NULL,
  user_id int(11) NOT NULL,
  card_number int(11) NOT NULL,
  expiration_date varchar(10) NOT NULL,
  cvv int(3) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla transactions
--

CREATE TABLE transactions (
  transaction_id int(11) NOT NULL,
  sender_user_id int(11) NOT NULL,
  received_user_id int(11) NOT NULL,
  amount int(11) NOT NULL,
  date date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla users
--

CREATE TABLE users (
  user_id int(10) NOT NULL,
  email varchar(80) NOT NULL,
  first_name varchar(50) NOT NULL,
  last_name varchar(50) NOT NULL,
  username varchar(20) NOT NULL,
  password varchar(20) NOT NULL,
  balance int(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Volcado de datos para la tabla users
--

INSERT INTO users (user_id, email, first_name, last_name, username, password, balance) VALUES
(10, 'Carlos@gmail.com', 'Carlos', 'Gomez', 'carlos_001', 123456, 10000);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla creditcards
--
ALTER TABLE creditcards
  ADD PRIMARY KEY (card_id);

--
-- Indices de la tabla transactions
--
ALTER TABLE transactions
  ADD PRIMARY KEY (transaction_id);

--
-- Indices de la tabla users
--
ALTER TABLE users
  ADD PRIMARY KEY (user_id);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla creditcards
--
ALTER TABLE creditcards
  MODIFY card_id int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla transactions
--
ALTER TABLE transactions
  MODIFY transaction_id int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla users
--
ALTER TABLE users
  MODIFY user_id int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;
