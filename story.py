class StoryMixin:

    def get_scene_story(self):
        if self.current_scene_index == 1:
            return [
                {"name": "Narrador",
                 "text": "En el reino de Oakhaven reinaba la paz y la tranquilidad en todo el valle. Sin embargo, todo cambió el fatídico día en que una misteriosa sombra cubrió el reino, sumiéndolo en la oscuridad.",
                 "portrait": None, "bg": self.bg_menu},
                {"name": "Narrador",
                 "text": "Mientras tanto, en el castillo real, comienza a circular un rumor inquietante: la princesa Leonor ha desaparecido sin dejar rastro.",
                 "portrait": None, "bg": self.bg_menu},
                {"name": "Narrador",
                 "text": "Con el paso del tiempo, la sombra se desvanece y el reino recupera su calma, pero queda una sensación de inquietud. Nadie sabe el paradero de la princesa. Miles de caballeros han salido en su búsqueda, pero ninguno regresó.",
                 "portrait": None, "bg": self.bg_menu},
                {"name": "Rey",
                 "text": "Antiguo caballero... Sé que juraste colgar tu espada y tu escudo tras la Gran Guerra. Pero mi hija es todo lo que tengo. Te suplico, encuéntrala y devuélvenos la paz.",
                 "portrait": self.img_king, "bg": self.bg_menu},
                {"name": "Caballero",
                 "text": "Hice una promesa solemne de no volver a derramar sangre. Sin embargo, ver a mi rey de rodillas rompe mi voluntad. Acepto. Esta será mi última misión.",
                 "portrait": self.img_knight, "bg": self.bg_menu},
                {"name": "Narrador",
                 "text": "Tras una larga y difícil búsqueda, llena de pistas falsas y caminos sin salida, el caballero descubre una extraña marca rúnica grabada en el puerto. Todo apunta a un único destino maldito: THE GREEN ISLAND.",
                 "portrait": None, "bg": self.bg_menu},
            ]

        elif self.current_scene_index == 2:
            return [
                {"name": "Narrador",
                 "text": "El protagonista llega en barco a la isla. Durante el trayecto marítimo, extrañas figuras acechan en la densa niebla, atacando los costados del navío hasta alcanzar las costas.",
                 "portrait": None, "bg": self.bg_jungle},
                {"name": "Caballero",
                 "text": "Por fin... The Green Island. El puerto está desierto y cubierto de vegetación salvaje. Siento ojos vigilándome desde la jungla.",
                 "portrait": self.img_knight, "bg": self.bg_jungle},
                {"name": "Guardián del Puerto",
                 "text": "¡Alto ahí, intruso! El amo prohibió que cualquier caballero profanara esta costa. Tu viaje termina en estas arenas húmedas.",
                 "portrait": self.img_boss1, "bg": self.bg_jungle},
                {"name": "Caballero",
                 "text": "Si pretendes bloquear mi camino hacia la princesa, desenvainar mi espada es lo último que lamentarás. ¡A defenderse!",
                 "portrait": self.img_knight, "bg": self.bg_jungle},
            ]

        elif self.current_scene_index == 3:
            return [
                {"name": "Narrador",
                 "text": "Tras derrotar al Guardián, el caballero se interna en la ciénaga densa de la isla. El aire se vuelve pesado y la magia del entorno distorsiona las sombras.",
                 "portrait": None, "bg": self.bg_swamp},
                {"name": "Caballero",
                 "text": "Este escudo mejorado bloquea cualquier impacto directo, pero siento que la magia aquí requiere algo más rápido... una evasión mágica.",
                 "portrait": self.img_knight, "bg": self.bg_swamp},
                {"name": "Mago Magaxo",
                 "text": "Jajaja... Veo que superaste al bruto del puerto. Pero mi magia arcana desintegrará tu armadura de metal reluciente. ¡Es inútil que intentes bloquearme!",
                 "portrait": self.img_boss2, "bg": self.bg_swamp},
                {"name": "Caballero",
                 "text": "He combatido hechiceros antes, Magaxo. Tu magia no me asusta. ¡Veamos qué tan rápido eres!",
                 "portrait": self.img_knight, "bg": self.bg_swamp},
            ]

        elif self.current_scene_index == 4:
            return [
                {"name": "Narrador",
                 "text": "Siguiendo el rastro, la altitud se eleva. La ciénaga da paso a un paso montañoso de rocas afiladas y vientos gélidos. El caballero está cada vez más cerca.",
                 "portrait": None, "bg": self.bg_mountain},
                {"name": "Caballero",
                 "text": "Con la habilidad de teletransportación puedo esquivar ataques mortales en un instante. Pero presiento que mi espada básica no le hará mella a lo que viene.",
                 "portrait": self.img_knight, "bg": self.bg_mountain},
                {"name": "Gólem de Piedra",
                 "text": "*RUIDO DE ROCAS MOVIÉNDOSE* ... INTRUSO... EL AMO ORDENA... ELIMINAR... CABALLERO...",
                 "portrait": self.img_boss3, "bg": self.bg_mountain},
                {"name": "Caballero",
                 "text": "¡Esa colosal mole de piedra me aplastará si me descuido! Necesito algo explosivo para agrietar su defensa.",
                 "portrait": self.img_knight, "bg": self.bg_mountain},
            ]

        elif self.current_scene_index == 5:
            return [
                {"name": "Narrador",
                 "text": "Finalmente, las pistas de runas y las marcas oscuras conducen a una gigantesca cueva basáltica en lo más profundo de la isla. Un aura tenebrosa emana del interior.",
                 "portrait": None, "bg": self.bg_cave},
                {"name": "Caballero",
                 "text": "Esta cueva... se siente extrañamente familiar. Siento una energía idéntica a la mía, pero totalmente corrompida por el odio.",
                 "portrait": self.img_knight, "bg": self.bg_cave},
                {"name": "Caballero Oscuro",
                 "text": "Te he estado esperando, viejo hipócrita. Mírate, luchando por un rey que te desechó. Yo soy tu verdad. Tu reflejo. Todo lo que reprimiste.",
                 "portrait": self.img_boss4, "bg": self.bg_cave},
                {"name": "Caballero Oscuro",
                 "text": "Yo soy el jefe supremo de The Green Island porque soy la encarnación de toda la culpa, la ira y la sangre que derramaste en la Gran Guerra. Al colgar tu espada creíste escapar, pero yo absorbí el poder oscuro de esta isla para gobernar las sombras y castigar tu hipocresía.",
                 "portrait": self.img_boss4, "bg": self.bg_cave},
                {"name": "Caballero Oscuro",
                 "text": "¡Yo soy el jefe final porque yo soy tu verdadero y definitivo destino! ¡Es hora de que enfrentes a tu propio pasado!",
                 "portrait": self.img_boss4, "bg": self.bg_cave},
                {"name": "Caballero",
                 "text": "¡No eres más que una ilusión nacida de mis remordimientos! Salvaré a la princesa y me liberaré de mi pasado de una vez por todas.",
                 "portrait": self.img_knight, "bg": self.bg_cave},
            ]

        elif self.current_scene_index == 6:
            return [
                {"name": "Narrador",
                 "text": "Tras una épica y brutal batalla, el caballero clava su espada en el corazón de su sombra. Con un alarido sordo, el Caballero Oscuro se disuelve en cenizas, liberando el alma del héroe.",
                 "portrait": None, "bg": self.bg_ending},
                {"name": "Narrador",
                 "text": "De repente, las sombras del fondo de la cueva se retiran. El misterioso vendedor encapuchado camina hacia la luz y, finalmente, se quita la capucha.",
                 "portrait": None, "bg": self.bg_ending},
                {"name": "Caballero",
                 "text": "¡Tú! Dijiste que te revelarías al final de mi camino. ¡Muestra tu rostro de una vez!",
                 "portrait": self.img_knight, "bg": self.bg_ending},
                {"name": "Hermano",
                 "text": "*Sonríe con tristeza* Ha pasado mucho tiempo, hermano menor... Pensaste que había muerto en la Gran Guerra, ¿verdad?",
                 "portrait": self.img_merchant, "bg": self.bg_ending},
                {"name": "Caballero",
                 "text": "¡¿Hermano?! ¡¿Tú estabas detrás de todo esto?! ¿Cómo es posible que sigas con vida en este lugar maldito?",
                 "portrait": self.img_knight, "bg": self.bg_ending},
                {"name": "Hermano",
                 "text": "No estoy vivo... La maldición de la isla consumió mi alma física hace años. Pero cuando supe que el Rey te enviaría aquí a morir, decidí usar lo último de mi poder para guiarte en secreto como vendedor. Las mejoras gratis eran el único modo de que vencieras a tu sombra.",
                 "portrait": self.img_merchant, "bg": self.bg_ending},
                {"name": "Hermano",
                 "text": "Ahora que has derrotado a tu oscuridad, mi alma finalmente es libre de descansar en paz. Ve, salva a la princesa Leonor y dile al Rey que cumpliste con tu deber. Regresa a casa por ambos...",
                 "portrait": self.img_merchant, "bg": self.bg_ending},
                {"name": "Narrador",
                 "text": "El hermano se disuelve lentamente en partículas de luz dorada, dejando una sonrisa de paz. El caballero, con lágrimas en los ojos, avanza para liberar a la princesa Leonor.",
                 "portrait": None, "bg": self.bg_ending},
                {"name": "Princesa Leonor",
                 "text": "¡Oh, noble caballero! He presenciado todo. Tu hermano sacrificó su alma eterna para protegerte y guiarte en las sombras. La maldición de la isla se ha disipado gracias a vuestro lazo familiar.",
                 "portrait": self.img_knight, "bg": self.bg_ending},
                {"name": "Caballero",
                 "text": "No fue una victoria mía solo... Fue nuestra. Vuestra alteza, el reino os espera. Regresemos a casa.",
                 "portrait": self.img_knight, "bg": self.bg_ending},
                {"name": "Narrador",
                 "text": "El caballero regresa victorioso a Oakhaven. El pueblo estalla en alegría y el rey premia al héroe. Con su deber cumplido, el caballero retira sus armas para siempre, cerrando su leyenda en paz. FIN.",
                 "portrait": None, "bg": self.bg_ending},
            ]
        return []

    def get_pre_shop_story(self, phase):
        if phase == 1:
            return [
                {"name": "Narrador",
                 "text": "El Guardián del Puerto cae de rodillas y se disuelve en el viento salado. De repente, una figura encapuchada surge de la espesura del bosque...",
                 "portrait": None, "bg": self.bg_jungle},
                {"name": "Caballero",
                 "text": "¿Quién está ahí? ¡Identifícate! ¿Eres otro de los esbirros de la sombra?",
                 "portrait": self.img_knight, "bg": self.bg_jungle},
                {"name": "Hombre Sospechoso",
                 "text": "*Risa ronca y baja* Jeje... No temas, noble caballero. Solo soy un humilde mercader atrapado en este lugar maldito. Veo que necesitas mejorar ese viejo escudo si quieres sobrevivir a lo que viene.",
                 "portrait": self.img_merchant, "bg": self.bg_jungle},
                {"name": "Caballero",
                 "text": "¿Cómo sabes a qué he venido? Tu rostro me resulta extrañamente familiar bajo esa capucha... ¿Quién eres en realidad?",
                 "portrait": self.img_knight, "bg": self.bg_jungle},
                {"name": "Hombre Sospechoso",
                 "text": "Eso no importa ahora. El peligro acecha en cada rincón. Toma estas runas para tu escudo... de forma gratis... por ahora. Jeje...",
                 "portrait": self.img_merchant, "bg": self.bg_jungle},
            ]
        elif phase == 2:
            return [
                {"name": "Narrador",
                 "text": "El Mago Magaxo grita mientras su bastón arcano estalla en mil pedazos. Mientras el humo se disipa, el hombre misterioso de la capucha vuelve a aparecer entre las sombras del pantano.",
                 "portrait": None, "bg": self.bg_swamp},
                {"name": "Caballero",
                 "text": "Tú otra vez... ¿Me estás siguiendo? ¿Cómo es posible que te muevas por este pantano maldito sin que las bestias te toquen?",
                 "portrait": self.img_knight, "bg": self.bg_swamp},
                {"name": "Hombre Sospechoso",
                 "text": "Esta isla tiene muchos caminos ocultos... para quienes saben dónde buscar. La magia de Magaxo controlaba la distorsión del espacio. Permíteme canalizar esa energía para darte una habilidad de evasión mágica...",
                 "portrait": self.img_merchant, "bg": self.bg_swamp},
                {"name": "Caballero",
                 "text": "Insisto, tu voz... tu postura... Siento que te conozco de hace mucho tiempo. ¿Por qué me estás ayudando?",
                 "portrait": self.img_knight, "bg": self.bg_swamp},
                {"name": "Hombre Sospechoso",
                 "text": "Digamos que tengo un interés muy personal en ver si logras llegar con vida al final de esta pesadilla. Elige tu teletransporte... y apresúrate.",
                 "portrait": self.img_merchant, "bg": self.bg_swamp},
            ]
        elif phase == 3:
            return [
                {"name": "Narrador",
                 "text": "El Gólem de piedra se derrumba en una avalancha de escombros. El suelo tiembla, y entre el polvo de piedra, el vendedor misterioso aguarda en silencio.",
                 "portrait": None, "bg": self.bg_mountain},
                {"name": "Caballero",
                 "text": "La cueva final del Caballero Oscuro está justo adelante. No puedes seguir ocultándote tras esa capucha. Háblame de una vez, ¿cuál es tu verdadero papel en esta maldición?",
                 "portrait": self.img_knight, "bg": self.bg_mountain},
                {"name": "Hombre Sospechoso",
                 "text": "*Su tono se vuelve melancólico por un instante* Mi papel es ayudarte a terminar lo que empezamos... o morir en el intento. La cueva final está sellada. Estas bombas te abrirán el camino.",
                 "portrait": self.img_merchant, "bg": self.bg_mountain},
                {"name": "Caballero",
                 "text": "Esta será la última batalla. Si sobrevivo, espero que me reveles tu verdadero rostro.",
                 "portrait": self.img_knight, "bg": self.bg_mountain},
                {"name": "Hombre Sospechoso",
                 "text": "Así será... si vives para contarlo. Elige tu explosivo.",
                 "portrait": self.img_merchant, "bg": self.bg_mountain},
            ]
        return []

    def get_shop_choices(self):
        if self.current_scene_index == 2:
            return [
                {"id": "spiked",
                 "title": "Escudo de Espinas",
                 "desc": "Bloquea el 100% del daño recibido y devuelve un 50% del daño bloqueado al atacante.",
                 "cost": "Gratis"},
                {"id": "rejuvenating",
                 "title": "Escudo Rejuvenecedor",
                 "desc": "Bloquea el 100% del daño y regenera 10 de vida (HP) al bloquear con éxito.",
                 "cost": "Gratis"},
            ]
        elif self.current_scene_index == 3:
            return [
                {"id": "counter",
                 "title": "Teletransporte de Contraataque",
                 "desc": "Esquiva el siguiente ataque y realiza un contraataque inmediato infligiendo 20 de daño.",
                 "cost": "Gratis"},
                {"id": "recharge",
                 "title": "Teletransporte de Recarga",
                 "desc": "Esquiva el ataque enemigo y recarga +2 puntos de energía extra.",
                 "cost": "Gratis"},
            ]
        elif self.current_scene_index == 4:
            return [
                {"id": "fire",
                 "title": "Bomba Ígnea",
                 "desc": "La bomba hace 40 de daño base y aplica Quemadura en el jefe (10 de daño por 3 turnos).",
                 "cost": "Gratis"},
                {"id": "mega",
                 "title": "Gran Mega Bomba",
                 "desc": "Incrementa el daño de la bomba a 75 de daño explosivo instantáneo al siguiente turno.",
                 "cost": "Gratis"},
            ]
        return []

    def select_shop_upgrade(self, upgrade_id):
        if self.current_scene_index == 2:
            self.shield_upgrade = upgrade_id
        elif self.current_scene_index == 3:
            self.tp_upgrade = upgrade_id
        elif self.current_scene_index == 4:
            self.bomb_upgrade = upgrade_id
